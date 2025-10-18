from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import statistics
import math
from datetime import datetime, timedelta

@dataclass
class FeatureImprovement:
    feature: str
    improvement: float
    confidence: float
    products_involved: List[str]
    time_period: str
    recommendation: str

@dataclass
class ProductFeatureImpact:
    product_id: str
    product_name: str
    feature_impacts: Dict[str, float]  # feature -> improvement score
    overall_effectiveness: float
    confidence_score: float
    usage_days: int
    recommendation: str

@dataclass
class SmartInsight:
    insight_type: str  # 'product_working', 'product_harming', 'missing_opportunity', 'routine_optimization'
    title: str
    description: str
    confidence: float
    evidence: List[str]
    actionable: bool
    priority: str  # 'high', 'medium', 'low'

class FeatureCorrelationAnalyzer:
    def __init__(self):
        self.feature_weights = {
            'dark_circles': {'vitamin_c_serum': 0.8, 'retinol': 0.6, 'niacinamide_serum': 0.7, 'sunscreen': 0.3},
            'puffiness': {'niacinamide_serum': 0.8, 'caffeine_serum': 0.9, 'retinol': 0.5, 'sunscreen': 0.2},
            'brightness': {'vitamin_c_serum': 0.9, 'aha_exfoliant': 0.8, 'retinol': 0.7, 'sunscreen': 0.4},
            'wrinkles': {'retinol': 0.9, 'peptide_serum': 0.8, 'sunscreen': 0.6, 'vitamin_c_serum': 0.5},
            'texture': {'aha_exfoliant': 0.9, 'bha_exfoliant': 0.8, 'retinol': 0.7, 'niacinamide_serum': 0.6}
        }
        
        self.product_categories = {
            'vitamin_c_serum': 'brightening',
            'retinol': 'anti_aging',
            'niacinamide_serum': 'pore_control',
            'sunscreen': 'protection',
            'aha_exfoliant': 'exfoliation',
            'bha_exfoliant': 'exfoliation',
            'peptide_serum': 'anti_aging',
            'hyaluronic_acid': 'hydration',
            'moisturizer': 'hydration',
            'cleanser': 'basic_care'
        }
    
    def analyze_feature_product_correlations(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze correlations between specific products and facial feature improvements
        """
        print("🔬 [FEATURE CORRELATION] Analyzing product-feature correlations...")
        
        if len(historical_data) < 3:
            return {
                "insufficient_data": True,
                "message": "Need at least 3 data points for feature correlation analysis"
            }
        
        # Sort data by date
        sorted_data = sorted(historical_data, key=lambda x: x.get('date', ''))
        
        # Analyze each feature
        feature_improvements = self._analyze_feature_improvements(sorted_data)
        
        # Analyze product impacts
        product_impacts = self._analyze_product_impacts(sorted_data)
        
        # Generate smart insights
        smart_insights = self._generate_smart_insights(feature_improvements, product_impacts, sorted_data)
        
        # Calculate trust metrics
        trust_metrics = self._calculate_trust_metrics(sorted_data, feature_improvements, product_impacts)
        
        return {
            "insufficient_data": False,
            "feature_improvements": [improvement.__dict__ for improvement in feature_improvements],
            "product_impacts": [impact.__dict__ for impact in product_impacts],
            "smart_insights": [insight.__dict__ for insight in smart_insights],
            "trust_metrics": trust_metrics,
            "analysis_period": {
                "start_date": sorted_data[0].get('date'),
                "end_date": sorted_data[-1].get('date'),
                "total_days": len(sorted_data)
            }
        }
    
    def _analyze_feature_improvements(self, data: List[Dict]) -> List[FeatureImprovement]:
        """Analyze improvements in each facial feature"""
        print("📊 [FEATURE CORRELATION] Analyzing feature improvements...")
        
        improvements = []
        features = ['dark_circles', 'puffiness', 'brightness', 'wrinkles', 'texture']
        
        for feature in features:
            improvement = self._calculate_feature_improvement(feature, data)
            if improvement:
                improvements.append(improvement)
        
        return improvements
    
    def _calculate_feature_improvement(self, feature: str, data: List[Dict]) -> Optional[FeatureImprovement]:
        """Calculate improvement for a specific feature"""
        if len(data) < 3:
            return None
        
        # Get feature values over time
        feature_values = []
        for entry in data:
            features = entry.get('features', {})
            if feature in features:
                feature_values.append({
                    'date': entry.get('date'),
                    'value': features[feature],
                    'routine': entry.get('routine', {})
                })
        
        if len(feature_values) < 3:
            return None
        
        # Calculate improvement trend
        early_values = feature_values[:len(feature_values)//2]
        recent_values = feature_values[len(feature_values)//2:]
        
        early_avg = statistics.mean([v['value'] for v in early_values])
        recent_avg = statistics.mean([v['value'] for v in recent_values])
        improvement = recent_avg - early_avg
        
        # Identify products that might be contributing
        contributing_products = self._identify_contributing_products(feature, data)
        
        # Calculate confidence based on data consistency
        confidence = self._calculate_confidence(feature_values, improvement)
        
        # Generate recommendation
        recommendation = self._generate_feature_recommendation(feature, improvement, contributing_products)
        
        return FeatureImprovement(
            feature=feature,
            improvement=round(improvement, 1),
            confidence=round(confidence, 2),
            products_involved=contributing_products,
            time_period=f"{len(feature_values)} days",
            recommendation=recommendation
        )
    
    def _identify_contributing_products(self, feature: str, data: List[Dict]) -> List[str]:
        """Identify products that might be contributing to feature improvement"""
        products = []
        
        # Get products used during the analysis period
        all_products = set()
        for entry in data:
            routine = entry.get('routine', {})
            skincare_products = routine.get('skincare_products', [])
            product_used_text = routine.get('product_used', '')
            
            # Extract products
            if skincare_products:
                all_products.update(skincare_products)
            if product_used_text:
                # Simple keyword extraction
                text_lower = product_used_text.lower()
                if 'vitamin c' in text_lower:
                    all_products.add('vitamin_c_serum')
                if 'retinol' in text_lower:
                    all_products.add('retinol')
                if 'sunscreen' in text_lower:
                    all_products.add('sunscreen')
                if 'moisturizer' in text_lower:
                    all_products.add('moisturizer')
                if 'niacinamide' in text_lower:
                    all_products.add('niacinamide_serum')
                if 'aha' in text_lower:
                    all_products.add('aha_exfoliant')
                if 'bha' in text_lower:
                    all_products.add('bha_exfoliant')
        
        # Check which products are likely contributing to this feature
        contributing = []
        for product in all_products:
            if product in self.feature_weights.get(feature, {}):
                weight = self.feature_weights[feature][product]
                if weight > 0.5:  # High correlation threshold
                    contributing.append(product)
        
        return contributing
    
    def _calculate_confidence(self, feature_values: List[Dict], improvement: float) -> float:
        """Calculate confidence score for the improvement"""
        if len(feature_values) < 3:
            return 0.0
        
        # Calculate consistency of improvement
        values = [v['value'] for v in feature_values]
        if len(values) < 2:
            return 0.0
        
        # Calculate trend consistency
        improvements = []
        for i in range(1, len(values)):
            improvements.append(values[i] - values[i-1])
        
        if not improvements:
            return 0.0
        
        # Consistency score based on how often improvement direction is maintained
        positive_improvements = sum(1 for imp in improvements if imp > 0)
        consistency = positive_improvements / len(improvements)
        
        # Magnitude score based on improvement size
        magnitude = min(1.0, abs(improvement) / 50.0)  # Normalize to 0-1
        
        # Data quality score based on number of data points
        data_quality = min(1.0, len(feature_values) / 10.0)  # Normalize to 0-1
        
        # Combined confidence score
        confidence = (consistency * 0.4 + magnitude * 0.4 + data_quality * 0.2)
        return min(1.0, confidence)
    
    def _generate_feature_recommendation(self, feature: str, improvement: float, products: List[str]) -> str:
        """Generate recommendation for feature improvement"""
        feature_names = {
            'dark_circles': 'dark circles',
            'puffiness': 'puffiness',
            'brightness': 'skin brightness',
            'wrinkles': 'wrinkles',
            'texture': 'skin texture'
        }
        
        feature_name = feature_names.get(feature, feature)
        
        if improvement > 10:
            if products:
                return f"Excellent! Your {feature_name} improved by {improvement:.1f} points. Your {', '.join(products)} routine is working well."
            else:
                return f"Great progress! Your {feature_name} improved by {improvement:.1f} points. Keep up your current routine."
        elif improvement > 5:
            if products:
                return f"Good improvement! Your {feature_name} got better by {improvement:.1f} points. Your {', '.join(products)} is helping."
            else:
                return f"Your {feature_name} improved by {improvement:.1f} points. Consider adding targeted products for better results."
        elif improvement < -10:
            if products:
                return f"Your {feature_name} got worse by {abs(improvement):.1f} points. Consider adjusting your {', '.join(products)} routine."
            else:
                return f"Your {feature_name} declined by {abs(improvement):.1f} points. Consider adding products to address this concern."
        elif improvement < -5:
            if products:
                return f"Your {feature_name} slightly declined by {abs(improvement):.1f} points. Monitor your {', '.join(products)} usage."
            else:
                return f"Your {feature_name} declined by {abs(improvement):.1f} points. Consider adding targeted treatments."
        else:
            if products:
                return f"Your {feature_name} is stable. Your {', '.join(products)} routine is maintaining it well."
            else:
                return f"Your {feature_name} is stable. Consider adding products for improvement."
    
    def _analyze_product_impacts(self, data: List[Dict]) -> List[ProductFeatureImpact]:
        """Analyze how each product impacts different features"""
        print("🔍 [FEATURE CORRELATION] Analyzing product impacts...")
        
        # Group data by products used
        product_usage = defaultdict(list)
        
        for entry in data:
            routine = entry.get('routine', {})
            skincare_products = routine.get('skincare_products', [])
            product_used_text = routine.get('product_used', '')
            
            # Extract products
            products = self._extract_products(skincare_products, product_used_text)
            
            for product in products:
                product_usage[product].append({
                    'date': entry.get('date'),
                    'features': entry.get('features', {}),
                    'skin_score': entry.get('skin_health_score', 0)
                })
        
        impacts = []
        for product_id, usage_data in product_usage.items():
            if len(usage_data) < 2:
                continue
            
            impact = self._calculate_product_impact(product_id, usage_data)
            if impact:
                impacts.append(impact)
        
        return impacts
    
    def _extract_products(self, skincare_products: List[str], product_used_text: str) -> List[str]:
        """Extract product IDs from both formats"""
        products = []
        
        if skincare_products:
            products.extend(skincare_products)
        
        if product_used_text:
            text_lower = product_used_text.lower()
            if 'vitamin c' in text_lower:
                products.append('vitamin_c_serum')
            if 'retinol' in text_lower:
                products.append('retinol')
            if 'sunscreen' in text_lower:
                products.append('sunscreen')
            if 'moisturizer' in text_lower:
                products.append('moisturizer')
            if 'niacinamide' in text_lower:
                products.append('niacinamide_serum')
            if 'aha' in text_lower:
                products.append('aha_exfoliant')
            if 'bha' in text_lower:
                products.append('bha_exfoliant')
            if 'hyaluronic' in text_lower:
                products.append('hyaluronic_acid')
            if 'peptide' in text_lower:
                products.append('peptide_serum')
        
        return list(set(products))
    
    def _calculate_product_impact(self, product_id: str, usage_data: List[Dict]) -> Optional[ProductFeatureImpact]:
        """Calculate impact of a specific product on different features"""
        if len(usage_data) < 2:
            return None
        
        # Sort by date
        usage_data.sort(key=lambda x: x['date'])
        
        # Calculate before/after for each feature
        features = ['dark_circles', 'puffiness', 'brightness', 'wrinkles', 'texture']
        feature_impacts = {}
        
        for feature in features:
            values = [entry['features'].get(feature, 0) for entry in usage_data if feature in entry['features']]
            if len(values) < 2:
                continue
            
            # Calculate improvement
            early_avg = statistics.mean(values[:len(values)//2])
            recent_avg = statistics.mean(values[len(values)//2:])
            improvement = recent_avg - early_avg
            feature_impacts[feature] = improvement
        
        if not feature_impacts:
            return None
        
        # Calculate overall effectiveness
        overall_effectiveness = statistics.mean(feature_impacts.values())
        
        # Calculate confidence based on consistency
        confidence = self._calculate_product_confidence(usage_data, feature_impacts)
        
        # Generate recommendation
        recommendation = self._generate_product_recommendation(product_id, feature_impacts, overall_effectiveness)
        
        return ProductFeatureImpact(
            product_id=product_id,
            product_name=self._get_product_display_name(product_id),
            feature_impacts=feature_impacts,
            overall_effectiveness=round(overall_effectiveness, 1),
            confidence_score=round(confidence, 2),
            usage_days=len(usage_data),
            recommendation=recommendation
        )
    
    def _calculate_product_confidence(self, usage_data: List[Dict], feature_impacts: Dict[str, float]) -> float:
        """Calculate confidence score for product impact"""
        if len(usage_data) < 3:
            return 0.5
        
        # Calculate consistency across features
        positive_impacts = sum(1 for impact in feature_impacts.values() if impact > 0)
        total_impacts = len(feature_impacts)
        consistency = positive_impacts / total_impacts if total_impacts > 0 else 0.5
        
        # Calculate magnitude of impact
        avg_impact = statistics.mean(feature_impacts.values())
        magnitude = min(1.0, abs(avg_impact) / 30.0)  # Normalize to 0-1
        
        # Calculate data quality
        data_quality = min(1.0, len(usage_data) / 7.0)  # Normalize to 0-1
        
        # Combined confidence
        confidence = (consistency * 0.4 + magnitude * 0.4 + data_quality * 0.2)
        return min(1.0, confidence)
    
    def _generate_product_recommendation(self, product_id: str, feature_impacts: Dict[str, float], overall_effectiveness: float) -> str:
        """Generate recommendation for product usage"""
        product_name = self._get_product_display_name(product_id)
        
        if overall_effectiveness > 10:
            # Identify which features improved most
            best_features = [f for f, imp in feature_impacts.items() if imp > 5]
            if best_features:
                feature_names = {
                    'dark_circles': 'dark circles',
                    'puffiness': 'puffiness',
                    'brightness': 'brightness',
                    'wrinkles': 'wrinkles',
                    'texture': 'texture'
                }
                improved_features = [feature_names.get(f, f) for f in best_features]
                return f"Excellent! {product_name} is working very well for your {', '.join(improved_features)}. Keep using it consistently."
            else:
                return f"Excellent! {product_name} is showing great overall results. Keep using it consistently."
        elif overall_effectiveness > 5:
            return f"Good results! {product_name} is helping your skin. Continue using it."
        elif overall_effectiveness < -10:
            return f"Consider discontinuing {product_name} - it may not be suitable for your skin type."
        elif overall_effectiveness < -5:
            return f"{product_name} isn't showing expected results. Consider adjusting usage or trying alternatives."
        else:
            return f"{product_name} is maintaining your skin. Monitor for longer-term effects."
    
    def _get_product_display_name(self, product_id: str) -> str:
        """Get display name for product"""
        names = {
            'vitamin_c_serum': 'Vitamin C Serum',
            'retinol': 'Retinol',
            'sunscreen': 'Sunscreen',
            'moisturizer': 'Moisturizer',
            'niacinamide_serum': 'Niacinamide Serum',
            'aha_exfoliant': 'AHA Exfoliant',
            'bha_exfoliant': 'BHA Exfoliant',
            'hyaluronic_acid': 'Hyaluronic Acid',
            'peptide_serum': 'Peptide Serum'
        }
        return names.get(product_id, product_id.replace('_', ' ').title())
    
    def _generate_smart_insights(self, feature_improvements: List[FeatureImprovement], 
                                product_impacts: List[ProductFeatureImpact], 
                                data: List[Dict]) -> List[SmartInsight]:
        """Generate smart insights based on analysis"""
        print("💡 [FEATURE CORRELATION] Generating smart insights...")
        
        insights = []
        
        # High-confidence insights
        high_confidence_improvements = [imp for imp in feature_improvements if imp.confidence > 0.7]
        for improvement in high_confidence_improvements:
            if improvement.improvement > 10:
                insights.append(SmartInsight(
                    insight_type='product_working',
                    title=f'{improvement.feature.replace("_", " ").title()} Improvement',
                    description=f"Your {improvement.feature.replace('_', ' ')} improved by {improvement.improvement:.1f} points. {improvement.recommendation}",
                    confidence=improvement.confidence,
                    evidence=[f"Data from {improvement.time_period}", f"Products: {', '.join(improvement.products_involved)}"],
                    actionable=True,
                    priority='high'
                ))
        
        # Product effectiveness insights
        effective_products = [p for p in product_impacts if p.overall_effectiveness > 10 and p.confidence_score > 0.7]
        for product in effective_products:
            insights.append(SmartInsight(
                insight_type='product_working',
                title=f'{product.product_name} is Working',
                description=product.recommendation,
                confidence=product.confidence_score,
                evidence=[f"Used for {product.usage_days} days", f"Overall effectiveness: {product.overall_effectiveness}"],
                actionable=True,
                priority='high'
            ))
        
        # Underperforming products
        underperforming = [p for p in product_impacts if p.overall_effectiveness < -5 and p.confidence_score > 0.6]
        for product in underperforming:
            insights.append(SmartInsight(
                insight_type='product_harming',
                title=f'{product.product_name} Not Working',
                description=product.recommendation,
                confidence=product.confidence_score,
                evidence=[f"Used for {product.usage_days} days", f"Overall effectiveness: {product.overall_effectiveness}"],
                actionable=True,
                priority='high'
            ))
        
        return insights
    
    def _calculate_trust_metrics(self, data: List[Dict], feature_improvements: List[FeatureImprovement], 
                                product_impacts: List[ProductFeatureImpact]) -> Dict[str, Any]:
        """Calculate trust metrics for the analysis"""
        total_data_points = len(data)
        high_confidence_insights = len([imp for imp in feature_improvements if imp.confidence > 0.7])
        effective_products = len([p for p in product_impacts if p.overall_effectiveness > 5])
        
        # Calculate data quality score
        data_quality = min(1.0, total_data_points / 10.0)
        
        # Calculate insight confidence
        avg_confidence = statistics.mean([imp.confidence for imp in feature_improvements]) if feature_improvements else 0.0
        
        # Calculate trust score
        trust_score = (data_quality * 0.4 + avg_confidence * 0.4 + (high_confidence_insights / max(1, len(feature_improvements))) * 0.2)
        
        return {
            "trust_score": round(trust_score, 2),
            "data_quality": round(data_quality, 2),
            "avg_confidence": round(avg_confidence, 2),
            "high_confidence_insights": high_confidence_insights,
            "effective_products": effective_products,
            "total_insights": len(feature_improvements) + len(product_impacts)
        }

# Global instance
feature_correlation_analyzer = FeatureCorrelationAnalyzer()
