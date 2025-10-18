"""
Weekly Analysis Service - Provides comprehensive weekly insights and trends
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from historical_data_service import historical_data_service
from trend_analysis_service import trend_analysis_service
from feature_correlation_analyzer import feature_correlation_analyzer

class WeeklyAnalysisService:
    def __init__(self):
        self.historical_service = historical_data_service
        self.trend_service = trend_analysis_service
        self.correlation_analyzer = feature_correlation_analyzer
    
    async def get_weekly_analysis(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive weekly analysis with trends and insights"""
        try:
            # Get historical data for the week
            historical_data = self.historical_service.get_user_history(user_id, days)
            
            if not historical_data or len(historical_data) < 2:
                return self._get_insufficient_data_response()
            
            # Sort by date (oldest first)
            historical_data.sort(key=lambda x: x.get('date', ''))
            
            # Calculate weekly trends
            trends = self._calculate_weekly_trends(historical_data)
            
            # Get routine effectiveness
            routine_effectiveness = await self.trend_service.analyze_routine_effectiveness(user_id, historical_data)
            
            # Get smart product analysis
            smart_analysis = self.correlation_analyzer.analyze_feature_product_correlations(historical_data)
            
            # Generate weekly summary
            weekly_summary = self._generate_weekly_summary(trends, routine_effectiveness, smart_analysis)
            
            # Generate weekly insights
            weekly_insights = self._generate_weekly_insights(trends, routine_effectiveness, smart_analysis)
            
            # Generate weekly recommendations
            weekly_recommendations = self._generate_weekly_recommendations(trends, routine_effectiveness, smart_analysis)
            
            return {
                "weekly_summary": weekly_summary,
                "weekly_insights": weekly_insights,
                "weekly_recommendations": weekly_recommendations,
                "trends": trends,
                "routine_effectiveness": routine_effectiveness,
                "smart_analysis": smart_analysis,
                "analysis_period": f"Last {len(historical_data)} days",
                "data_points": len(historical_data)
            }
            
        except Exception as e:
            print(f"❌ [WEEKLY ANALYSIS] Error: {e}")
            return self._get_error_response(str(e))
    
    def _calculate_weekly_trends(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """Calculate weekly trends from historical data"""
        if len(historical_data) < 2:
            return {"insufficient_data": True}
        
        # Calculate score trends
        sleep_scores = [entry.get('sleep_score', 0) for entry in historical_data]
        skin_scores = [entry.get('skin_health_score', 0) for entry in historical_data]
        
        # Calculate improvements
        sleep_improvement = sleep_scores[-1] - sleep_scores[0] if len(sleep_scores) > 1 else 0
        skin_improvement = skin_scores[-1] - skin_scores[0] if len(skin_scores) > 1 else 0
        
        # Calculate average scores
        avg_sleep = sum(sleep_scores) / len(sleep_scores)
        avg_skin = sum(skin_scores) / len(skin_scores)
        
        # Calculate feature trends
        feature_trends = {}
        features = ['dark_circles', 'puffiness', 'brightness', 'wrinkles', 'texture']
        
        for feature in features:
            feature_values = []
            for entry in historical_data:
                if 'features' in entry and feature in entry['features']:
                    feature_values.append(entry['features'][feature])
            
            if len(feature_values) > 1:
                improvement = feature_values[-1] - feature_values[0]
                feature_trends[feature] = {
                    'improvement': improvement,
                    'current': feature_values[-1],
                    'average': sum(feature_values) / len(feature_values),
                    'trend': 'improving' if improvement > 5 else 'declining' if improvement < -5 else 'stable'
                }
        
        return {
            'sleep_improvement': sleep_improvement,
            'skin_improvement': skin_improvement,
            'avg_sleep_score': avg_sleep,
            'avg_skin_score': avg_skin,
            'feature_trends': feature_trends,
            'total_days': len(historical_data),
            'score_consistency': self._calculate_consistency(sleep_scores, skin_scores)
        }
    
    def _calculate_consistency(self, sleep_scores: List[float], skin_scores: List[float]) -> str:
        """Calculate how consistent the scores are"""
        if len(sleep_scores) < 3:
            return "insufficient_data"
        
        sleep_variance = sum((score - sum(sleep_scores)/len(sleep_scores))**2 for score in sleep_scores) / len(sleep_scores)
        skin_variance = sum((score - sum(skin_scores)/len(skin_scores))**2 for score in skin_scores) / len(skin_scores)
        
        avg_variance = (sleep_variance + skin_variance) / 2
        
        if avg_variance < 50:
            return "very_consistent"
        elif avg_variance < 100:
            return "consistent"
        elif avg_variance < 200:
            return "variable"
        else:
            return "inconsistent"
    
    def _generate_weekly_summary(self, trends: Dict, routine_effectiveness: Dict, smart_analysis: Dict) -> str:
        """Generate weekly summary based on trends and analysis"""
        if trends.get('insufficient_data'):
            return "Take more selfies this week to get your weekly analysis!"
        
        sleep_improvement = trends.get('sleep_improvement', 0)
        skin_improvement = trends.get('skin_improvement', 0)
        consistency = trends.get('score_consistency', 'variable')
        
        summary_parts = []
        
        # Overall progress
        if sleep_improvement > 5 and skin_improvement > 5:
            summary_parts.append(f"Great week! Your sleep improved by {sleep_improvement:.1f} points and skin health by {skin_improvement:.1f} points.")
        elif sleep_improvement > 0 or skin_improvement > 0:
            summary_parts.append(f"Positive progress this week - sleep improved by {sleep_improvement:.1f} points, skin by {skin_improvement:.1f} points.")
        elif sleep_improvement < -5 or skin_improvement < -5:
            summary_parts.append(f"Challenging week - sleep declined by {abs(sleep_improvement):.1f} points, skin by {abs(skin_improvement):.1f} points.")
        else:
            summary_parts.append("Stable week with consistent scores.")
        
        # Consistency
        if consistency == "very_consistent":
            summary_parts.append("Your routine is very consistent - keep it up!")
        elif consistency == "inconsistent":
            summary_parts.append("Your scores are quite variable - consider establishing a more consistent routine.")
        
        return " ".join(summary_parts)
    
    def _generate_weekly_insights(self, trends: Dict, routine_effectiveness: Dict, smart_analysis: Dict) -> List[str]:
        """Generate weekly insights based on analysis"""
        insights = []
        
        if trends.get('insufficient_data'):
            return ["Take more selfies this week to get personalized insights!"]
        
        # Smart skincare product analysis
        if not smart_analysis.get('insufficient_data', True):
            product_impacts = smart_analysis.get('product_impacts', [])
            smart_insights = smart_analysis.get('smart_insights', [])
            
            # Product effectiveness insights
            for impact in product_impacts:
                if impact.get('confidence_score', 0) > 0.6:
                    product_name = impact.get('product_name', '')
                    effectiveness = impact.get('overall_effectiveness', 0)
                    feature_impacts = impact.get('feature_impacts', {})
                    
                    if effectiveness > 15:
                        # Find which features improved most
                        best_features = [f for f, score in feature_impacts.items() if score > 10]
                        if best_features:
                            feature_names = [f.replace('_', ' ').title() for f in best_features]
                            insights.append(f"• {product_name} is working great! It's improving your {', '.join(feature_names)}")
                        else:
                            insights.append(f"• {product_name} is showing excellent results - keep using it!")
                    elif effectiveness > 5:
                        insights.append(f"• {product_name} is helping your skin - consider using it more consistently")
                    elif effectiveness < -5:
                        insights.append(f"• {product_name} might not be the right fit for your skin - consider switching")
            
            # Smart insights from correlation analysis
            for insight in smart_insights:
                if insight.get('confidence', 0) > 0.7 and insight.get('actionable', False):
                    insights.append(f"• {insight.get('description', '')}")
        
        # Feature improvement insights with product context
        feature_trends = trends.get('feature_trends', {})
        for feature, data in feature_trends.items():
            if data['trend'] == 'improving' and data['improvement'] > 10:
                feature_name = feature.replace('_', ' ').title()
                # Check if we have product correlation data
                if not smart_analysis.get('insufficient_data', True):
                    product_impacts = smart_analysis.get('product_impacts', [])
                    related_products = []
                    for impact in product_impacts:
                        if impact.get('feature_impacts', {}).get(feature, 0) > 5:
                            related_products.append(impact.get('product_name', ''))
                    
                    if related_products:
                        insights.append(f"• {feature_name} improved by {data['improvement']:.1f} points - your {', '.join(related_products)} is working!")
                    else:
                        insights.append(f"• {feature_name} improved significantly this week (+{data['improvement']:.1f} points)")
                else:
                    insights.append(f"• {feature_name} improved significantly this week (+{data['improvement']:.1f} points)")
            elif data['trend'] == 'declining' and data['improvement'] < -10:
                feature_name = feature.replace('_', ' ').title()
                insights.append(f"• {feature_name} declined this week ({data['improvement']:.1f} points) - consider adjusting your routine")
        
        # Routine insights
        if routine_effectiveness.get('overall_trend') == 'improving':
            insights.append("• Your overall routine is showing positive results - keep it up!")
        elif routine_effectiveness.get('overall_trend') == 'declining':
            insights.append("• Your routine needs adjustment - consider trying different products or habits")
        
        # Consistency insights
        consistency = trends.get('score_consistency', 'variable')
        if consistency == 'very_consistent':
            insights.append("• Your routine is very consistent - this is great for long-term results!")
        elif consistency == 'inconsistent':
            insights.append("• Your scores vary a lot - try to maintain a more consistent routine")
        
        return insights if insights else ["Keep tracking your routine to get more insights!"]
    
    def _generate_weekly_recommendations(self, trends: Dict, routine_effectiveness: Dict, smart_analysis: Dict) -> List[str]:
        """Generate weekly recommendations based on analysis"""
        recommendations = []
        
        if trends.get('insufficient_data'):
            return ["Take more selfies this week to get personalized recommendations!"]
        
        # Smart skincare product recommendations
        if not smart_analysis.get('insufficient_data', True):
            product_impacts = smart_analysis.get('product_impacts', [])
            smart_insights = smart_analysis.get('smart_insights', [])
            
            # Product effectiveness recommendations
            for impact in product_impacts:
                if impact.get('confidence_score', 0) > 0.6:
                    product_name = impact.get('product_name', '')
                    effectiveness = impact.get('overall_effectiveness', 0)
                    feature_impacts = impact.get('feature_impacts', {})
                    
                    if effectiveness > 15:
                        # Recommend continuing or increasing usage
                        best_features = [f for f, score in feature_impacts.items() if score > 10]
                        if best_features:
                            feature_names = [f.replace('_', ' ').title() for f in best_features]
                            recommendations.append(f"Keep using {product_name} - it's great for your {', '.join(feature_names)}")
                        else:
                            recommendations.append(f"Continue using {product_name} - it's showing excellent results")
                    elif effectiveness > 5:
                        recommendations.append(f"Use {product_name} more consistently - it's helping your skin")
                    elif effectiveness < -5:
                        recommendations.append(f"Consider switching from {product_name} - it may not be right for your skin type")
            
            # Smart insights recommendations
            for insight in smart_insights:
                if insight.get('confidence', 0) > 0.7 and insight.get('actionable', False):
                    recommendations.append(insight.get('description', ''))
        
        # Score-based recommendations
        sleep_improvement = trends.get('sleep_improvement', 0)
        skin_improvement = trends.get('skin_improvement', 0)
        
        if sleep_improvement < -5:
            recommendations.append("Focus on improving sleep quality - your sleep scores declined this week")
        elif sleep_improvement > 5:
            recommendations.append("Great sleep progress! Continue your current sleep routine")
        
        if skin_improvement < -5:
            recommendations.append("Your skin health declined - consider adjusting your skincare routine")
        elif skin_improvement > 5:
            recommendations.append("Excellent skin progress! Your current routine is working well")
        
        # Feature-specific recommendations with product suggestions
        feature_trends = trends.get('feature_trends', {})
        for feature, data in feature_trends.items():
            if data['trend'] == 'declining' and data['improvement'] < -10:
                feature_name = feature.replace('_', ' ').title()
                # Suggest products for specific features
                if feature == 'dark_circles':
                    recommendations.append(f"Address {feature_name} - try adding a vitamin C serum or eye cream with caffeine")
                elif feature == 'puffiness':
                    recommendations.append(f"Address {feature_name} - try a niacinamide serum or caffeine-based eye treatment")
                elif feature == 'brightness':
                    recommendations.append(f"Address {feature_name} - try a vitamin C serum or AHA exfoliant")
                elif feature == 'wrinkles':
                    recommendations.append(f"Address {feature_name} - try a retinol serum or peptide treatment")
                elif feature == 'texture':
                    recommendations.append(f"Address {feature_name} - try an AHA or BHA exfoliant")
                else:
                    recommendations.append(f"Address {feature_name} - it declined significantly this week")
        
        return recommendations if recommendations else ["Keep up your current routine and track progress!"]
    
    def _get_insufficient_data_response(self) -> Dict[str, Any]:
        """Return response when there's insufficient data"""
        return {
            "weekly_summary": "Take more selfies this week to get your weekly analysis!",
            "weekly_insights": ["Take more selfies this week to get personalized insights!"],
            "weekly_recommendations": ["Take more selfies this week to get personalized recommendations!"],
            "trends": {"insufficient_data": True},
            "routine_effectiveness": {"insufficient_data": True},
            "smart_analysis": {"insufficient_data": True},
            "analysis_period": "Insufficient data",
            "data_points": 0
        }
    
    def _get_error_response(self, error: str) -> Dict[str, Any]:
        """Return error response"""
        return {
            "weekly_summary": f"Error generating weekly analysis: {error}",
            "weekly_insights": ["Unable to generate insights at this time"],
            "weekly_recommendations": ["Unable to generate recommendations at this time"],
            "trends": {"error": True},
            "routine_effectiveness": {"error": True},
            "smart_analysis": {"error": True},
            "analysis_period": "Error",
            "data_points": 0
        }

# Global instance
weekly_analysis_service = WeeklyAnalysisService()
