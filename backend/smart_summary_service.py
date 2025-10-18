"""
Smart Summary Service with LLM Integration
- Uses existing LLM service for intelligent recommendations
- Data-driven trend analysis for insights
- Fallback to rule-based if LLM fails
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics
from llm_service import FlexibleLLMService


@dataclass
class FeatureTrend:
    """Represents the trend for a specific facial feature"""
    feature_name: str
    current_value: float
    previous_value: float
    change: float
    change_percentage: float
    trend: str  # 'improving', 'declining', 'stable', 'stagnant'
    duration_days: int
    significance: str  # 'significant', 'moderate', 'minor', 'none'


@dataclass
class TrendInsight:
    """Insights generated from trend analysis"""
    feature: str
    insight: str
    priority: int  # 1 (highest) to 5 (lowest)
    category: str  # 'positive', 'concern', 'neutral'


class SmartSummaryService:
    """
    Data-driven smart summary generation based on historical trends
    Implements the 5-step methodology:
    1. Data Collection (already handled by HistoricalDataService)
    2. Trend Analysis
    3. Change Detection and Thresholds
    4. Duration Monitoring
    5. Summary Generation
    """
    
    def __init__(self):
        # Step 3: Define thresholds for change detection
        self.IMPROVEMENT_THRESHOLD = 2.0  # Points increase considered improvement
        self.DECLINE_THRESHOLD = -2.0     # Points decrease considered decline
        self.STAGNATION_THRESHOLD = 0.5   # Less than this = stagnant
        
        # Step 4: Duration thresholds
        self.STAGNATION_DURATION = 14     # Days without improvement = stagnant
        self.TREND_CONFIRMATION_PERIOD = 7  # Days to confirm a trend
        
        # Feature score ranges (0-100 scale from ai_engine.py)
        self.FEATURE_RANGES = {
            'dark_circles': {'excellent': 75, 'good': 60, 'fair': 45, 'poor': 30},
            'puffiness': {'excellent': 70, 'good': 55, 'fair': 40, 'poor': 25},
            'brightness': {'excellent': 80, 'good': 65, 'fair': 50, 'poor': 35},
            'wrinkles': {'excellent': 75, 'good': 60, 'fair': 45, 'poor': 30},
            'texture': {'excellent': 75, 'good': 60, 'fair': 45, 'poor': 30},
            'pore_size': {'excellent': 70, 'good': 55, 'fair': 40, 'poor': 25}
        }
        
        # Feature display names
        self.FEATURE_NAMES = {
            'dark_circles': 'Dark Circles',
            'puffiness': 'Eye Puffiness',
            'brightness': 'Skin Brightness',
            'wrinkles': 'Fine Lines',
            'texture': 'Skin Texture',
            'pore_size': 'Pore Size'
        }
        
        # Initialize LLM service for AI-powered summaries
        self.llm_service = FlexibleLLMService()
    
    async def generate_smart_summary(
        self, 
        current_analysis: Dict[str, Any],
        routine: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive smart summary based on data trends
        
        Args:
            current_analysis: Today's analysis result
            routine: Today's routine data
            historical_data: Historical analysis data (sorted by date)
        
        Returns:
            Smart summary with insights and recommendations
        """
        print(f"🧠 [SMART SUMMARY] Generating hybrid summary (local analysis + AI recommendations)...")
        print(f"📊 [SMART SUMMARY] Historical data points: {len(historical_data)}")
        
        # TEMPORARY FOR TESTING: Always use AI even with no historical data
        # TODO: Revert this after testing OpenAI integration
        if len(historical_data) < 2:
            print(f"⚠️ [TESTING MODE] No historical data, but forcing AI call for testing...")
            
            # Generate actual insights based on current analysis
            features = current_analysis.get('features', {})
            sleep_score = current_analysis.get('sleep_score', 0)
            skin_score = current_analysis.get('skin_health_score', 0)
            
            # Generate meaningful insights - always show 2 lowest features
            insights = []
            
            # Find lowest 2 features
            sorted_features = sorted(features.items(), key=lambda x: x[1])[:2]
            
            for feature_key, value in sorted_features:
                feature_name = self.FEATURE_NAMES.get(feature_key, feature_key)
                insights.append(f"{feature_name}: {value:.0f}/100 - looks good but can improve")
            
            # Generate AI recommendations
            try:
                print(f"🤖 [AI] Generating intelligent recommendations (TESTING MODE)...")
                rec_result = await self._generate_ai_recommendations(
                    current_analysis, routine, [], [], []
                )
                # Handle both dict and list formats
                if isinstance(rec_result, dict):
                    recommendations = rec_result.get('recommendations', [])
                    natural_remedies = rec_result.get('natural_remedies', [])
                    product_recs = rec_result.get('product_recommendations', [])
                    lifestyle_tip = rec_result.get('lifestyle_tip')
                else:
                    recommendations = rec_result if isinstance(rec_result, list) else []
                    natural_remedies = []
                    product_recs = []
                    lifestyle_tip = None
            except Exception as e:
                print(f"⚠️ [AI] Failed in testing mode: {e}")
                recommendations = ["📊 Take daily selfies to track trends"]
                natural_remedies = []
                product_recs = []
                lifestyle_tip = None
            
            return {
                "daily_summary": f"Welcome! Your baseline Sleep Score is {sleep_score} and Skin Health Score is {skin_score}. Keep taking daily selfies to track your progress! 🌟",
                "key_insights": insights[:5],
                "recommendations": recommendations[:6],
                "natural_remedies": natural_remedies,
                "product_recommendations": product_recs,
                "lifestyle_tip": lifestyle_tip,
                "trend_analysis": {"improving_features": [], "declining_features": [], "stagnant_features": [], "stable_features": list(features.keys())},
                "model": "Hybrid (Local + AI) - TESTING MODE",
                "provider": "internal + LLM",
                "data_points_analyzed": len(historical_data)
            }
        
        # LOCAL ANALYSIS (Fast, reliable, free)
        # Step 2: Perform trend analysis
        feature_trends = self._analyze_feature_trends(current_analysis, historical_data)
        
        # Step 3 & 4: Detect changes and monitor duration
        significant_changes = self._detect_significant_changes(feature_trends)
        stagnant_features = self._detect_stagnation(historical_data, current_analysis)
        
        # Step 5a: Generate daily summary (local)
        daily_summary = self._generate_daily_summary(
            current_analysis, feature_trends, significant_changes, stagnant_features, routine
        )
        
        # Step 5b: Generate key insights (local)
        key_insights = self._generate_key_insights(
            feature_trends, significant_changes, stagnant_features
        )
        
        # Step 5c: AI-POWERED RECOMMENDATIONS (Smart, professional)
        print(f"🤖 [AI] Generating intelligent recommendations...")
        rec_result = await self._generate_ai_recommendations(
            current_analysis, routine, feature_trends, stagnant_features, significant_changes
        )
        
        # Handle both dict and list formats
        if isinstance(rec_result, dict):
            recommendations = rec_result.get('recommendations', [])
            natural_remedies = rec_result.get('natural_remedies', [])
            product_recs = rec_result.get('product_recommendations', [])
            lifestyle_tip = rec_result.get('lifestyle_tip')
        else:
            recommendations = rec_result if isinstance(rec_result, list) else []
            natural_remedies = []
            product_recs = []
            lifestyle_tip = None
        
        return {
            "daily_summary": daily_summary,
            "key_insights": key_insights,
            "recommendations": recommendations,
            "natural_remedies": natural_remedies,
            "product_recommendations": product_recs,
            "lifestyle_tip": lifestyle_tip,
            "trend_analysis": {
                "improving_features": [t.feature_name for t in feature_trends if t.trend == 'improving'],
                "declining_features": [t.feature_name for t in feature_trends if t.trend == 'declining'],
                "stagnant_features": stagnant_features,
                "stable_features": [t.feature_name for t in feature_trends if t.trend == 'stable']
            },
            "model": "Hybrid (Local + AI)",
            "provider": "internal + LLM",
            "data_points_analyzed": len(historical_data)
        }
    
    def _analyze_feature_trends(
        self, 
        current_analysis: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> List[FeatureTrend]:
        """Step 2: Analyze trends for each feature using statistical methods"""
        trends = []
        current_features = current_analysis.get('features', {})
        
        # Get comparison period (last 7 days average vs previous 7 days)
        if len(historical_data) >= 7:
            recent_period = historical_data[-7:]
            comparison_period = historical_data[-14:-7] if len(historical_data) >= 14 else historical_data[:7]
        else:
            recent_period = historical_data
            comparison_period = historical_data[:len(historical_data)//2] if len(historical_data) > 1 else historical_data[:1]
        
        for feature_key, current_value in current_features.items():
            # Calculate average values for comparison
            recent_avg = statistics.mean([
                entry.get('features', {}).get(feature_key, 0) 
                for entry in recent_period
            ])
            
            if comparison_period:
                previous_avg = statistics.mean([
                    entry.get('features', {}).get(feature_key, 0) 
                    for entry in comparison_period
                ])
            else:
                previous_avg = current_value
            
            # Calculate change
            change = recent_avg - previous_avg
            change_percentage = (change / abs(previous_avg)) * 100 if previous_avg != 0 else 0
            
            # Determine trend
            if change >= self.IMPROVEMENT_THRESHOLD:
                trend = 'improving'
                significance = 'significant' if abs(change) >= 5 else 'moderate'
            elif change <= self.DECLINE_THRESHOLD:
                trend = 'declining'
                significance = 'significant' if abs(change) >= 5 else 'moderate'
            elif abs(change) <= self.STAGNATION_THRESHOLD:
                trend = 'stagnant'
                significance = 'none'
            else:
                trend = 'stable'
                significance = 'minor'
            
            trends.append(FeatureTrend(
                feature_name=feature_key,
                current_value=current_value,
                previous_value=previous_avg,
                change=change,
                change_percentage=change_percentage,
                trend=trend,
                duration_days=len(recent_period),
                significance=significance
            ))
        
        return trends
    
    def _detect_significant_changes(self, feature_trends: List[FeatureTrend]) -> List[FeatureTrend]:
        """Step 3: Detect significant changes based on thresholds"""
        return [
            trend for trend in feature_trends 
            if trend.significance in ['significant', 'moderate']
        ]
    
    def _detect_stagnation(
        self, 
        historical_data: List[Dict[str, Any]],
        current_analysis: Dict[str, Any]
    ) -> List[str]:
        """Step 4: Monitor duration and detect stagnant features"""
        stagnant_features = []
        
        if len(historical_data) < self.STAGNATION_DURATION:
            return stagnant_features
        
        # Check last 14 days for stagnation
        recent_period = historical_data[-self.STAGNATION_DURATION:]
        current_features = current_analysis.get('features', {})
        
        for feature_key in current_features.keys():
            # Get all values for this feature in the period
            values = [entry.get('features', {}).get(feature_key, 0) for entry in recent_period]
            
            if not values:
                continue
            
            # Calculate variance and change
            variance = statistics.variance(values) if len(values) > 1 else 0
            total_change = abs(values[-1] - values[0])
            
            # Feature is stagnant if:
            # 1. Low variance (not changing much)
            # 2. Total change is minimal
            # 3. Score is still in "poor" or "fair" range
            if variance < 2.0 and total_change < 2.0:
                feature_range = self.FEATURE_RANGES.get(feature_key, {})
                if current_features[feature_key] < feature_range.get('good', 60):
                    stagnant_features.append(feature_key)
        
        return stagnant_features
    
    def _generate_daily_summary(
        self,
        current_analysis: Dict[str, Any],
        feature_trends: List[FeatureTrend],
        significant_changes: List[FeatureTrend],
        stagnant_features: List[str],
        routine: Dict[str, Any]
    ) -> str:
        """Step 5: Generate overall status message based on trends"""
        sleep_score = current_analysis.get('sleep_score', 0)
        skin_score = current_analysis.get('skin_health_score', 0)
        
        # Count trend types
        improving = len([t for t in feature_trends if t.trend == 'improving'])
        declining = len([t for t in feature_trends if t.trend == 'declining'])
        
        # Generate status based on overall patterns
        if improving >= 3 and declining == 0:
            status = "Excellent progress! "
            message = f"Your Sleep Score is {sleep_score} and Skin Health is {skin_score}. Multiple features are improving—your routine is working beautifully! Keep going! 🌟"
        
        elif improving >= 2 and declining <= 1:
            status = "Good progress! "
            message = f"Sleep Score: {sleep_score}, Skin Health: {skin_score}. You're seeing positive changes in {improving} areas. Stay consistent with your routine! 💪"
        
        elif len(stagnant_features) >= 3:
            status = "Time for changes. "
            message = f"Sleep Score: {sleep_score}, Skin Health: {skin_score}. Some features have plateaued for 2+ weeks. Consider adjusting your routine for better results. 🔄"
        
        elif declining >= 2:
            status = "Needs attention. "
            message = f"Sleep Score: {sleep_score}, Skin Health: {skin_score}. {declining} features are declining. Review your sleep and skincare routine—something may need adjustment. ⚠️"
        
        else:
            status = "Steady progress. "
            message = f"Sleep Score: {sleep_score}, Skin Health: {skin_score}. Your routine is maintaining stability. Stay consistent for continued results! ✨"
        
        return status + message
    
    def _generate_key_insights(
        self,
        feature_trends: List[FeatureTrend],
        significant_changes: List[FeatureTrend],
        stagnant_features: List[str]
    ) -> List[str]:
        """Generate prioritized key insights"""
        insights = []
        
        # Significant improvements (Priority 1)
        for trend in significant_changes:
            if trend.trend == 'improving':
                feature_name = self.FEATURE_NAMES.get(trend.feature_name, trend.feature_name)
                insights.append(
                    f"🎉 {feature_name} improved by {abs(trend.change):.1f} points ({abs(trend.change_percentage):.0f}%) - your efforts are paying off!"
                )
        
        # Significant declines (Priority 2)
        for trend in significant_changes:
            if trend.trend == 'declining':
                feature_name = self.FEATURE_NAMES.get(trend.feature_name, trend.feature_name)
                insights.append(
                    f"⚠️ {feature_name} declined by {abs(trend.change):.1f} points - may need immediate attention"
                )
        
        # Stagnation alerts (Priority 3)
        for feature_key in stagnant_features:
            feature_name = self.FEATURE_NAMES.get(feature_key, feature_key)
            insights.append(
                f"🔄 {feature_name} hasn't improved in 2+ weeks - consider trying different products or methods"
            )
        
        # Excellent features (Priority 4)
        for trend in feature_trends:
            feature_range = self.FEATURE_RANGES.get(trend.feature_name, {})
            if trend.current_value >= feature_range.get('excellent', 75):
                feature_name = self.FEATURE_NAMES.get(trend.feature_name, trend.feature_name)
                if len(insights) < 5:  # Limit total insights
                    insights.append(
                        f"✨ {feature_name} is excellent ({trend.current_value:.0f}/100) - maintain your current routine!"
                    )
        
        return insights[:6]  # Return top 6 insights
    
    def _generate_recommendations(
        self,
        current_analysis: Dict[str, Any],
        feature_trends: List[FeatureTrend],
        stagnant_features: List[str],
        routine: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations based on trends"""
        recommendations = []
        current_features = current_analysis.get('features', {})
        
        # Recommendations for declining features
        declining = [t for t in feature_trends if t.trend == 'declining']
        for trend in declining[:2]:  # Top 2 declining features
            recs = self._get_feature_recommendations(trend.feature_name, 'declining', current_features.get(trend.feature_name, 0), routine)
            recommendations.extend(recs)
        
        # Recommendations for stagnant features
        for feature_key in stagnant_features[:2]:  # Top 2 stagnant features
            recs = self._get_feature_recommendations(feature_key, 'stagnant', current_features.get(feature_key, 0), routine)
            recommendations.extend(recs)
        
        # General lifestyle recommendations
        sleep_hours = routine.get('sleep_hours', 0)
        water_intake = routine.get('water_intake', 0)
        
        if sleep_hours < 7:
            recommendations.append(f"🛏️ Aim for 7-8 hours of sleep tonight (currently {sleep_hours}h) - critical for skin recovery")
        
        if water_intake < 6:
            recommendations.append(f"💧 Increase water intake to 8+ glasses (currently {water_intake}) for better hydration")
        
        # Product recommendations for improving features
        improving = [t for t in feature_trends if t.trend == 'improving']
        if improving:
            best_feature = max(improving, key=lambda t: abs(t.change))
            recommendations.append(
                f"✅ Continue your current routine - it's working well for {self.FEATURE_NAMES.get(best_feature.feature_name)}!"
            )
        
        return recommendations[:8]  # Top 8 recommendations
    
    async def _generate_ai_recommendations(
        self,
        current_analysis: Dict[str, Any],
        routine: Dict[str, Any],
        feature_trends: List[FeatureTrend],
        stagnant_features: List[str],
        significant_changes: List[FeatureTrend]
    ) -> List[str]:
        """
        Use AI (LLM) to generate intelligent, dermatologist-grade recommendations
        Falls back to rule-based if AI fails
        """
        try:
            # Get worst 2 features for targeted skincare recommendations
            features = current_analysis.get('features', {})
            sleep_score = current_analysis.get('sleep_score', 0)
            skin_score = current_analysis.get('skin_health_score', 0)
            
            worst = sorted(features.items(), key=lambda x: x[1])[:2]
            area1_key = worst[0][0] if len(worst) > 0 else "skin_health"
            area2_key = worst[1][0] if len(worst) > 1 else "texture"
            area1 = self.FEATURE_NAMES.get(area1_key, area1_key)
            area2 = self.FEATURE_NAMES.get(area2_key, area2_key)
            value1 = worst[0][1] if len(worst) > 0 else 0
            value2 = worst[1][1] if len(worst) > 1 else 0
            
            # Create a unique context to force varied responses
            import random
            variation_seed = random.choice([
                "Focus on innovative skincare",
                "Emphasize dermatologist-approved methods",
                "Prioritize evidence-based approaches",
                "Consider holistic skin wellness"
            ])
            
            prompt = f"""{variation_seed} for {area1} ({value1}/100) and {area2} ({value2}/100).

STRICT RULES:
- NO sleep advice (we handle that separately)
- NO water/hydration advice
- NO food/diet suggestions
- Give ONLY topical skincare solutions

Give 4 recommendations IN THIS ORDER:
1. Natural/DIY remedy for {area1} (e.g., "Apply aloe vera gel for 20 minutes")
2. Natural/DIY remedy for {area2} (e.g., "Use cold spoons on eyes")
3. Product with ingredient for {area1} (e.g., "Try vitamin C serum 15-20%")
4. Product with ingredient for {area2} (e.g., "Use caffeine eye cream")

Be specific with ingredients, percentages, times. Write as short direct sentences."""

            # Try to get AI response using existing LLM service
            ai_response = await self.llm_service.generate_smart_summary(
                analysis_data=current_analysis,
                routine_data=routine,
                historical_data=[{"prompt": prompt}]
            )
            
            # Extract AI recommendations (skincare only)
            if ai_response and isinstance(ai_response, dict):
                ai_recs = ai_response.get('recommendations', [])
                print(f"🔍 [DEBUG] AI response has {len(ai_recs)} skincare recommendations")
                if ai_recs and len(ai_recs) >= 1:
                    print(f"✅ [AI] Using {len(ai_recs)} AI skincare recommendations")
                    print(f"📋 [AI SKINCARE RECOMMENDATIONS]:")
                    for i, rec in enumerate(ai_recs[:4], 1):
                        print(f"  {i}. {rec}")
                    
                    # Add rule-based lifestyle recommendation (just 1)
                    lifestyle_rec = self._get_lifestyle_recommendation(routine)
                    if lifestyle_rec:
                        print(f"📋 [RULE-BASED LIFESTYLE RECOMMENDATION]:")
                        print(f"  5. {lifestyle_rec}")
                    
                    # Get separated arrays from AI response
                    natural_rems = ai_response.get('natural_remedies', [])
                    product_recs = ai_response.get('product_recommendations', [])
                    
                    # Combine: AI skincare (4) + lifestyle (1) = 5 total
                    combined = ai_recs[:4]
                    if lifestyle_rec:
                        combined.append(lifestyle_rec)
                    
                    # Return both combined and separated
                    return {
                        'recommendations': combined,
                        'natural_remedies': natural_rems[:2],
                        'product_recommendations': product_recs[:2],
                        'lifestyle_tip': lifestyle_rec
                    }
                else:
                    print(f"⚠️ [AI] No recommendations in response: {list(ai_response.keys())}")
            
            # Fallback to rule-based
            print(f"⚠️ [AI] Falling back to rule-based recommendations")
            raise Exception("AI recommendations not available")
            
        except Exception as e:
            print(f"⚠️ [AI] Recommendation generation failed: {e}")
            print(f"📊 [FALLBACK] Using rule-based recommendations...")
            
            # FALLBACK: Use rule-based recommendations
            recommendations = []
            
            # Recommendations for declining features
            declining = [t for t in feature_trends if t.trend == 'declining']
            for trend in declining[:2]:
                recs = self._get_feature_recommendations(
                    trend.feature_name, 'declining', 
                    trend.current_value, routine
                )
                recommendations.extend(recs)
            
            # Recommendations for stagnant features
            for feature_key in stagnant_features[:2]:
                recs = self._get_feature_recommendations(
                    feature_key, 'stagnant',
                    current_analysis.get('features', {}).get(feature_key, 0),
                    routine
                )
                recommendations.extend(recs)
            
            # General lifestyle recommendations
            if routine.get('sleep_hours', 8) < 7:
                recommendations.append(
                    f"🛏️ Increase sleep to 7-8 hours (currently {routine.get('sleep_hours')}h) - critical for skin recovery and repair"
                )
            
            if routine.get('water_intake', 8) < 6:
                recommendations.append(
                    f"💧 Drink 8+ glasses of water daily (currently {routine.get('water_intake')}) for optimal skin hydration"
                )
            
            return recommendations[:8]
    
    def _get_feature_specific_guidance(self, feature1: str, feature2: str) -> str:
        """
        Get feature-specific guidance to help AI generate varied, relevant recommendations
        """
        guidance_map = {
            'dark_circles': "Consider vitamin K, caffeine, retinol, cold therapy, iron-rich diet, sleep position",
            'puffiness': "Consider jade roller, lymphatic drainage, cool compress, reduce sodium, elevate head while sleeping",
            'brightness': "Consider vitamin C serums, chemical exfoliants (AHA/BHA), sunscreen SPF 50+, antioxidants, kojic acid",
            'wrinkles': "Consider retinol/retinoids, peptides, hyaluronic acid, facial massage, sun protection",
            'texture': "Consider chemical exfoliants, niacinamide, salicylic acid, clay masks, gentle physical exfoliation",
            'pore_size': "Consider niacinamide, BHA (salicylic acid), clay masks, retinol, avoid heavy oils"
        }
        
        guidance1 = guidance_map.get(feature1, "Focus on overall skin health")
        guidance2 = guidance_map.get(feature2, "Maintain consistent skincare routine")
        
        return f"For {self.FEATURE_NAMES.get(feature1, feature1)}: {guidance1}\nFor {self.FEATURE_NAMES.get(feature2, feature2)}: {guidance2}"
    
    def _get_lifestyle_recommendation(self, routine: Dict[str, Any]) -> str:
        """
        Generate single rule-based lifestyle recommendation (prioritize sleep)
        Simple, token-free recommendation that doesn't need AI
        """
        sleep_hours = routine.get('sleep_hours', 0)
        water_intake = routine.get('water_intake', 0)
        
        # Prioritize sleep recommendations (most important for skin)
        if sleep_hours < 6:
            return "Prioritize getting 7-9 hours of quality sleep each night for optimal skin repair and regeneration."
        elif sleep_hours < 7:
            return f"Aim for an additional hour of sleep to reach the optimal 7-9 hours for better skin health."
        elif sleep_hours >= 7 and sleep_hours <= 9:
            return f"Great sleep routine! Continue maintaining {int(sleep_hours)} hours nightly to support your skin's natural recovery."
        elif water_intake < 6:
            # If sleep is good but water is low, mention water
            return "Increase water intake to 8+ glasses daily to improve skin hydration and flush out toxins."
        else:
            # If both are good, give general encouragement
            return "Keep up your healthy lifestyle habits – they're supporting your skin's natural glow!"
    
    def _get_severity_level(self, feature_key: str, value: float) -> str:
        """Get severity level label based on feature value and ranges"""
        feature_range = self.FEATURE_RANGES.get(feature_key, {})
        
        if value >= feature_range.get('excellent', 75):
            return "Excellent"
        elif value >= feature_range.get('good', 60):
            return "Good"
        elif value >= feature_range.get('fair', 45):
            return "Fair"
        elif value >= feature_range.get('poor', 30):
            return "Poor"
        else:
            return "Needs Attention"
    
    def _format_features_for_ai(self, features: Dict[str, float]) -> str:
        """Format features for AI prompt"""
        lines = []
        for key, value in sorted(features.items(), key=lambda x: x[1]):
            name = self.FEATURE_NAMES.get(key, key)
            severity = self._get_severity_level(key, value)
            lines.append(f"• {name}: {value:.0f}/100 ({severity})")
        return '\n'.join(lines)
    
    def _format_trends_for_ai(self, trends: List[FeatureTrend]) -> str:
        """Format trends for AI prompt"""
        if not trends:
            return "No historical data yet"
        
        lines = []
        for t in trends:
            name = self.FEATURE_NAMES.get(t.feature_name, t.feature_name)
            arrow = "↗️" if t.trend == 'improving' else "↘️" if t.trend == 'declining' else "→"
            lines.append(f"• {name}: {arrow} {t.change:+.1f} ({t.change_percentage:+.0f}%)")
        return '\n'.join(lines)
    
    def _format_problems_for_ai(self, problem_areas: List[tuple]) -> str:
        """Format problem areas for AI"""
        lines = []
        for key, value in problem_areas:
            name = self.FEATURE_NAMES.get(key, key)
            lines.append(f"• {name}: {value:.0f}/100 - needs attention")
        return '\n'.join(lines)
    
    def _get_feature_recommendations(
        self, 
        feature_key: str, 
        status: str,
        current_value: float,
        routine: Dict[str, Any]
    ) -> List[str]:
        """Simple fallback recommendations (AI handles the smart ones)"""
        recommendations = []
        feature_name = self.FEATURE_NAMES.get(feature_key, feature_key)
        
        if feature_key == 'dark_circles':
            if status == 'declining':
                recommendations.append(f"👁️ {feature_name} declining - prioritize 8+ hours sleep, use caffeine eye cream")
            else:
                recommendations.append(f"👁️ {feature_name} stagnant - try vitamin K serum or cold compress")
        
        elif feature_key == 'puffiness':
            if status == 'declining':
                recommendations.append(f"💧 {feature_name} worsening - reduce sodium, sleep elevated, increase water")
            else:
                recommendations.append(f"💧 {feature_name} stagnant - try ice roller, avoid salty foods")
        
        elif feature_key == 'brightness':
            if status == 'declining':
                recommendations.append(f"✨ {feature_name} declining - add vitamin C serum, use SPF 50+ daily")
            else:
                recommendations.append(f"✨ {feature_name} stagnant - try gentle exfoliation 2x/week")
        
        elif feature_key == 'wrinkles':
            if status == 'declining':
                recommendations.append(f"📏 {feature_name} worsening - consider retinol 0.3%, use SPF, hydrate well")
            else:
                recommendations.append(f"📏 {feature_name} stagnant - try peptide serum or increase retinol strength")
        
        elif feature_key == 'texture':
            if status == 'declining':
                recommendations.append(f"🧽 {feature_name} declining - use AHA/BHA exfoliant, add hyaluronic acid")
            else:
                recommendations.append(f"🧽 {feature_name} stagnant - try niacinamide 5-10% serum")
        
        elif feature_key == 'pore_size':
            if status == 'declining':
                recommendations.append(f"🔍 {feature_name} worsening - use salicylic acid cleanser, clay mask 2x/week")
            else:
                recommendations.append(f"🔍 {feature_name} stagnant - try niacinamide serum, double cleanse")
        
        return recommendations
    
    async def _generate_first_time_summary(
        self, 
        current_analysis: Dict[str, Any],
        routine: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate summary for first-time users with no historical data"""
        sleep_score = current_analysis.get('sleep_score', 0)
        skin_score = current_analysis.get('skin_health_score', 0)
        features = current_analysis.get('features', {})
        
        # Find weakest areas
        sorted_features = sorted(features.items(), key=lambda x: x[1])
        weakest_features = sorted_features[:2]
        
        insights = [
            "📸 First analysis complete! We'll track your progress over time.",
            f"💤 Your Sleep Score is {sleep_score} and Skin Health Score is {skin_score}."
        ]
        
        # Add insights for weak areas
        for feature_key, value in weakest_features:
            feature_name = self.FEATURE_NAMES.get(feature_key, feature_key)
            feature_range = self.FEATURE_RANGES.get(feature_key, {})
            
            if value < feature_range.get('poor', 30):
                insights.append(f"⚠️ {feature_name} needs attention (score: {value:.0f})")
            elif value < feature_range.get('fair', 45):
                insights.append(f"🔍 {feature_name} has room for improvement (score: {value:.0f})")
        
        # Try AI recommendations even for first-time users
        print(f"🤖 [AI] Generating intelligent recommendations for first-time user...")
        try:
            recommendations = await self._generate_ai_recommendations(
                current_analysis, routine, [], [], []
            )
        except Exception as e:
            print(f"⚠️ [AI] Failed for first-time user, using fallback: {e}")
            # Fallback recommendations
            recommendations = [
                "📊 Take daily selfies to track trends and see what works for you",
                "💤 Aim for 7-8 hours of quality sleep each night",
                "💧 Stay hydrated with 8+ glasses of water daily"
            ]
            # Add specific recommendations for weak areas
            for feature_key, value in weakest_features:
                recs = self._get_feature_recommendations(feature_key, 'declining', value, routine)
                recommendations.extend(recs[:1])  # One rec per weak feature
        
        return {
            "daily_summary": f"Welcome! Your baseline Sleep Score is {sleep_score} and Skin Health Score is {skin_score}. Keep taking daily selfies to track your progress! 🌟",
            "key_insights": insights[:5],
            "recommendations": recommendations[:6],
            "trend_analysis": {
                "improving_features": [],
                "declining_features": [],
                "stagnant_features": [],
                "stable_features": list(features.keys())
            },
            "model": "Hybrid (Local + AI)",
            "provider": "internal + LLM",
            "data_points_analyzed": 1
        }


# Global instance
smart_summary_service = SmartSummaryService()
