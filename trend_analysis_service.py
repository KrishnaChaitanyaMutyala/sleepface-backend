from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import statistics
from dataclasses import dataclass
from collections import defaultdict
import json

@dataclass
class ProductEffectiveness:
    product_id: str
    product_name: str
    usage_days: int
    avg_skin_score_before: float
    avg_skin_score_after: float
    avg_sleep_score_before: float
    avg_sleep_score_after: float
    improvement_trend: str  # 'improving', 'declining', 'stable', 'no_data'
    effectiveness_score: float  # -100 to 100
    recommendation: str

@dataclass
class RoutineInsight:
    insight_type: str  # 'product_working', 'product_not_working', 'routine_optimization', 'missing_product'
    title: str
    description: str
    confidence: float
    actionable: bool
    products_involved: List[str]

class TrendAnalysisService:
    def __init__(self):
        self.min_data_points = 3  # Minimum data points needed for trend analysis
        self.lookback_days = 30   # Days to look back for analysis
        
    async def analyze_routine_effectiveness(self, user_id: str, historical_data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze the effectiveness of skincare routines over time
        """
        print(f"📊 [TREND ANALYSIS] Analyzing routine effectiveness for user: {user_id}")
        print(f"📊 [TREND ANALYSIS] Historical data points: {len(historical_data)}")
        
        if len(historical_data) < self.min_data_points:
            return {
                "insufficient_data": True,
                "message": f"Need at least {self.min_data_points} data points for trend analysis",
                "current_data_points": len(historical_data)
            }
        
        # Sort data by date
        sorted_data = sorted(historical_data, key=lambda x: x.get('date', ''))
        
        # Analyze product effectiveness
        product_effectiveness = self._analyze_product_effectiveness(sorted_data)
        
        # Generate routine insights
        routine_insights = self._generate_routine_insights(sorted_data, product_effectiveness)
        
        # Calculate overall trends
        overall_trends = self._calculate_overall_trends(sorted_data)
        
        # Generate recommendations
        recommendations = self._generate_trend_recommendations(product_effectiveness, routine_insights)
        
        return {
            "insufficient_data": False,
            "analysis_period": {
                "start_date": sorted_data[0].get('date'),
                "end_date": sorted_data[-1].get('date'),
                "total_days": len(sorted_data)
            },
            "product_effectiveness": [effect.__dict__ for effect in product_effectiveness],
            "routine_insights": [insight.__dict__ for insight in routine_insights],
            "overall_trends": overall_trends,
            "recommendations": recommendations
        }
    
    def _analyze_product_effectiveness(self, data: List[Dict]) -> List[ProductEffectiveness]:
        """Analyze how effective each product has been"""
        print("🔍 [TREND ANALYSIS] Analyzing product effectiveness...")
        
        # Group data by products used
        product_usage = defaultdict(list)
        
        for entry in data:
            routine = entry.get('routine', {})
            skincare_products = routine.get('skincare_products', [])
            product_used_text = routine.get('product_used', '')
            
            # Extract products from both new and legacy formats
            products = self._extract_products(skincare_products, product_used_text)
            
            for product in products:
                product_usage[product].append({
                    'date': entry.get('date'),
                    'sleep_score': entry.get('sleep_score', 0),
                    'skin_score': entry.get('skin_health_score', 0),
                    'features': entry.get('features', {})
                })
        
        effectiveness_results = []
        
        for product_id, usage_data in product_usage.items():
            if len(usage_data) < 2:  # Need at least 2 data points
                continue
                
            effectiveness = self._calculate_product_effectiveness(product_id, usage_data)
            if effectiveness:
                effectiveness_results.append(effectiveness)
        
        return effectiveness_results
    
    def _extract_products(self, skincare_products: List[str], product_used_text: str) -> List[str]:
        """Extract product IDs from both new and legacy formats"""
        products = []
        
        # Add from new format
        if skincare_products:
            products.extend(skincare_products)
        
        # Add from legacy format (simple text parsing)
        if product_used_text:
            # Simple keyword extraction for legacy format
            text_lower = product_used_text.lower()
            if 'vitamin c' in text_lower:
                products.append('vitamin_c_serum')
            if 'retinol' in text_lower:
                products.append('retinol')
            if 'sunscreen' in text_lower:
                products.append('sunscreen')
            if 'moisturizer' in text_lower:
                products.append('moisturizer')
            if 'hyaluronic' in text_lower:
                products.append('hyaluronic_acid')
            if 'niacinamide' in text_lower:
                products.append('niacinamide_serum')
        
        return list(set(products))  # Remove duplicates
    
    def _calculate_product_effectiveness(self, product_id: str, usage_data: List[Dict]) -> Optional[ProductEffectiveness]:
        """Calculate effectiveness of a specific product"""
        if len(usage_data) < 2:
            return None
        
        # Sort by date
        usage_data.sort(key=lambda x: x['date'])
        
        # Calculate before/after scores
        first_half = usage_data[:len(usage_data)//2]
        second_half = usage_data[len(usage_data)//2:]
        
        avg_skin_before = statistics.mean([entry['skin_score'] for entry in first_half])
        avg_skin_after = statistics.mean([entry['skin_score'] for entry in second_half])
        avg_sleep_before = statistics.mean([entry['sleep_score'] for entry in first_half])
        avg_sleep_after = statistics.mean([entry['sleep_score'] for entry in second_half])
        
        # Calculate improvement
        skin_improvement = avg_skin_after - avg_skin_before
        sleep_improvement = avg_sleep_after - avg_sleep_before
        
        # Determine trend
        if skin_improvement > 5:
            trend = 'improving'
        elif skin_improvement < -5:
            trend = 'declining'
        else:
            trend = 'stable'
        
        # Calculate effectiveness score (-100 to 100)
        effectiveness_score = min(100, max(-100, skin_improvement * 2))
        
        # Generate recommendation
        recommendation = self._generate_product_recommendation(
            product_id, trend, effectiveness_score, skin_improvement
        )
        
        return ProductEffectiveness(
            product_id=product_id,
            product_name=self._get_product_display_name(product_id),
            usage_days=len(usage_data),
            avg_skin_score_before=round(avg_skin_before, 1),
            avg_skin_score_after=round(avg_skin_after, 1),
            avg_sleep_score_before=round(avg_sleep_before, 1),
            avg_sleep_score_after=round(avg_sleep_after, 1),
            improvement_trend=trend,
            effectiveness_score=round(effectiveness_score, 1),
            recommendation=recommendation
        )
    
    def _generate_product_recommendation(self, product_id: str, trend: str, effectiveness_score: float, improvement: float) -> str:
        """Generate recommendation for a specific product"""
        product_name = self._get_product_display_name(product_id)
        
        if trend == 'improving':
            if effectiveness_score > 20:
                return f"Excellent! {product_name} is working very well for you. Keep using it consistently."
            else:
                return f"Good progress! {product_name} is showing positive results. Continue using it."
        elif trend == 'declining':
            if effectiveness_score < -20:
                return f"Consider discontinuing {product_name} - it may not be suitable for your skin."
            else:
                return f"{product_name} isn't showing expected results. Consider adjusting usage or trying alternatives."
        else:
            if effectiveness_score > 10:
                return f"{product_name} is maintaining your skin well. Continue using it."
            elif effectiveness_score < -10:
                return f"{product_name} isn't providing significant benefits. Consider alternatives."
            else:
                return f"{product_name} is stable. Monitor for longer-term effects."
    
    def _get_product_display_name(self, product_id: str) -> str:
        """Get display name for product ID"""
        product_names = {
            'vitamin_c_serum': 'Vitamin C Serum',
            'retinol': 'Retinol',
            'sunscreen': 'Sunscreen',
            'moisturizer': 'Moisturizer',
            'hyaluronic_acid': 'Hyaluronic Acid',
            'niacinamide_serum': 'Niacinamide Serum',
            'peptide_serum': 'Peptide Serum',
            'aha_exfoliant': 'AHA Exfoliant',
            'bha_exfoliant': 'BHA Exfoliant',
            'azelaic_acid': 'Azelaic Acid',
            'gentle_cleanser': 'Gentle Cleanser',
            'toner': 'Toner',
            'face_mask': 'Face Mask',
            'exfoliant': 'Exfoliant'
        }
        return product_names.get(product_id, product_id.replace('_', ' ').title())
    
    def _generate_routine_insights(self, data: List[Dict], product_effectiveness: List[ProductEffectiveness]) -> List[RoutineInsight]:
        """Generate insights about the overall routine"""
        print("💡 [TREND ANALYSIS] Generating routine insights...")
        
        insights = []
        
        # Find working products
        working_products = [p for p in product_effectiveness if p.improvement_trend == 'improving' and p.effectiveness_score > 10]
        if working_products:
            insights.append(RoutineInsight(
                insight_type='product_working',
                title='Products Working Well',
                description=f"Your {', '.join([p.product_name for p in working_products])} are showing positive results. Keep using them consistently.",
                confidence=0.8,
                actionable=True,
                products_involved=[p.product_id for p in working_products]
            ))
        
        # Find underperforming products
        underperforming = [p for p in product_effectiveness if p.improvement_trend == 'declining' and p.effectiveness_score < -10]
        if underperforming:
            insights.append(RoutineInsight(
                insight_type='product_not_working',
                title='Products Not Working',
                description=f"Consider discontinuing {', '.join([p.product_name for p in underperforming])} - they may not be suitable for your skin type.",
                confidence=0.7,
                actionable=True,
                products_involved=[p.product_id for p in underperforming]
            ))
        
        # Find stable products
        stable_products = [p for p in product_effectiveness if p.improvement_trend == 'stable']
        if stable_products:
            insights.append(RoutineInsight(
                insight_type='routine_optimization',
                title='Stable Products',
                description=f"Your {', '.join([p.product_name for p in stable_products])} are maintaining your skin. Consider adding new active ingredients for further improvement.",
                confidence=0.6,
                actionable=True,
                products_involved=[p.product_id for p in stable_products]
            ))
        
        return insights
    
    def _calculate_overall_trends(self, data: List[Dict]) -> Dict[str, Any]:
        """Calculate overall trends in skin and sleep scores"""
        print("📈 [TREND ANALYSIS] Calculating overall trends...")
        
        skin_scores = [entry.get('skin_health_score', 0) for entry in data]
        sleep_scores = [entry.get('sleep_score', 0) for entry in data]
        
        # Calculate trends
        skin_trend = self._calculate_trend(skin_scores)
        sleep_trend = self._calculate_trend(sleep_scores)
        
        # Calculate averages
        avg_skin = statistics.mean(skin_scores)
        avg_sleep = statistics.mean(sleep_scores)
        
        # Calculate improvement over time
        if len(skin_scores) >= 4:
            recent_skin = statistics.mean(skin_scores[-4:])  # Last 4 entries
            early_skin = statistics.mean(skin_scores[:4])    # First 4 entries
            skin_improvement = recent_skin - early_skin
        else:
            skin_improvement = 0
        
        if len(sleep_scores) >= 4:
            recent_sleep = statistics.mean(sleep_scores[-4:])
            early_sleep = statistics.mean(sleep_scores[:4])
            sleep_improvement = recent_sleep - early_sleep
        else:
            sleep_improvement = 0
        
        return {
            'skin_trend': skin_trend,
            'sleep_trend': sleep_trend,
            'avg_skin_score': round(avg_skin, 1),
            'avg_sleep_score': round(avg_sleep, 1),
            'skin_improvement': round(skin_improvement, 1),
            'sleep_improvement': round(sleep_improvement, 1)
        }
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend direction from a list of scores"""
        if len(scores) < 2:
            return 'insufficient_data'
        
        # Simple linear trend calculation
        first_half = scores[:len(scores)//2]
        second_half = scores[len(scores)//2:]
        
        avg_first = statistics.mean(first_half)
        avg_second = statistics.mean(second_half)
        
        improvement = avg_second - avg_first
        
        if improvement > 5:
            return 'improving'
        elif improvement < -5:
            return 'declining'
        else:
            return 'stable'
    
    def _generate_trend_recommendations(self, product_effectiveness: List[ProductEffectiveness], routine_insights: List[RoutineInsight]) -> List[str]:
        """Generate actionable recommendations based on trend analysis"""
        recommendations = []
        
        # Product-specific recommendations
        for product in product_effectiveness:
            if product.improvement_trend == 'improving' and product.effectiveness_score > 20:
                recommendations.append(f"Continue using {product.product_name} - it's showing excellent results!")
            elif product.improvement_trend == 'declining' and product.effectiveness_score < -20:
                recommendations.append(f"Consider replacing {product.product_name} with a different product")
            elif product.improvement_trend == 'stable' and product.effectiveness_score < 5:
                recommendations.append(f"Try increasing frequency or concentration of {product.product_name}")
        
        # General recommendations
        if not product_effectiveness:
            recommendations.append("Start tracking your skincare routine to see which products work best for you")
        
        # Add insights-based recommendations
        for insight in routine_insights:
            if insight.actionable:
                recommendations.append(insight.description)
        
        return recommendations[:5]  # Limit to 5 recommendations

# Global instance
trend_analysis_service = TrendAnalysisService()
