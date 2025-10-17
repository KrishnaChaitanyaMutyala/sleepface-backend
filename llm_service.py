"""
Flexible LLM Service - Supports multiple free and paid models
Easy to add new models and switch between them
"""
import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from enum import Enum

# Import the feature correlation analyzer
try:
    from feature_correlation_analyzer import feature_correlation_analyzer
except ImportError:
    feature_correlation_analyzer = None

class ModelType(Enum):
    RULE_BASED = "rule_based"
    HUGGINGFACE_FREE = "huggingface_free"
    OLLAMA_LOCAL = "ollama_local"
    OPENAI_FREE = "openai_free"
    ANTHROPIC_FREE = "anthropic_free"
    GROQ = "groq"
    GROK = "grok"
    CUSTOM_API = "custom_api"

class BaseLLMProvider(ABC):
    """Base class for all LLM providers"""
    
    @abstractmethod
    async def generate_summary(self, context: str, analysis_data: Dict) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    def _create_world_class_prompt(self, context: str, analysis_data: Dict) -> str:
        """Create a simple, clean prompt for Grok"""
        
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        features = analysis_data.get('features', {})
        
        prompt = f"""Skin Analysis - Focus on improvement areas and skincare suggestions:

Scores: Sleep {sleep_score}/100, Skin {skin_score}/100
Features: Dark Circles {features.get('dark_circles', 0):.1f}, Brightness {features.get('brightness', 0):.1f}, Wrinkles {features.get('wrinkles', 0):.1f}, Texture {features.get('texture', 0):.1f}, Pore Size {features.get('pore_size', 0):.1f}

Provide:
1. Key improvement areas (what needs work)
2. Specific skincare product recommendations
3. Lifestyle changes for better skin
4. Expected timeline for results

Keep it concise and actionable."""

        return prompt
    
    def _create_concise_prompt(self, context: str, analysis_data: Dict) -> str:
        """Create ultra-concise prompt for minimal token usage - 2-liner format"""
        
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        features = analysis_data.get('features', {})
        
        # Find worst 2 features
        sorted_features = sorted(features.items(), key=lambda x: x[1])[:2]
        worst_areas = ", ".join([f.replace('_', ' ') for f, _ in sorted_features])
        
        # ULTRA-MINIMAL prompt for speed
        prompt = f"""Sleep:{sleep_score} Skin:{skin_score} Low:{worst_areas}
2 lines: 1)condition 2)fix"""

        return prompt

    def _identify_focus_areas(self, features: Dict) -> str:
        """Identify top 3 focus areas based on scores"""
        sorted_features = sorted(features.items(), key=lambda x: x[1])
        focus_areas = [f.replace('_', ' ').title() for f, _ in sorted_features[:3]]
        return ", ".join(focus_areas)
    
    def _generate_dynamic_insights(self, features: Dict, routine: Dict) -> List[str]:
        """Generate dynamic, personalized insights based on actual feature scores"""
        insights = []
        
        # Get feature scores with more granular analysis
        dark_circles = features.get('dark_circles', 0)
        puffiness = features.get('puffiness', 0)
        brightness = features.get('brightness', 0)
        wrinkles = features.get('wrinkles', 0)
        texture = features.get('texture', 0)
        pore_size = features.get('pore_size', 0)
        
        # Dark Circles - More nuanced insights
        if dark_circles < 30:
            insights.append(f"Severe dark circles detected (score: {dark_circles:.1f}) - this suggests significant sleep debt or chronic fatigue")
        elif dark_circles < 45:
            insights.append(f"Prominent dark circles (score: {dark_circles:.1f}) - prioritize 8+ hours of sleep and consider eye cream with caffeine")
        elif dark_circles < 60:
            insights.append(f"Mild dark circles visible (score: {dark_circles:.1f}) - try cold compress and earlier bedtime")
        elif dark_circles > 75:
            insights.append(f"Excellent eye area condition (score: {dark_circles:.1f}) - your sleep routine is working beautifully!")
        
        # Puffiness - Contextual insights
        if puffiness < 25:
            insights.append(f"Significant eye puffiness (score: {puffiness:.1f}) - reduce salt intake, try sleeping elevated, and use cold therapy")
        elif puffiness < 40:
            insights.append(f"Moderate puffiness detected (score: {puffiness:.1f}) - stay hydrated and consider allergy evaluation")
        elif puffiness < 55:
            insights.append(f"Mild puffiness around eyes (score: {puffiness:.1f}) - maintain hydration and adequate sleep")
        elif puffiness > 70:
            insights.append(f"Excellent eye definition (score: {puffiness:.1f}) - great circulation and rest habits!")
        
        # Brightness - Comprehensive analysis
        if brightness < 30:
            insights.append(f"Skin appears very dull (score: {brightness:.1f}) - increase water intake, consider vitamin C serum, and check iron levels")
        elif brightness < 45:
            insights.append(f"Skin needs more radiance (score: {brightness:.1f}) - try gentle exfoliation, hydrating masks, and better lighting in photos")
        elif brightness < 60:
            insights.append(f"Skin brightness is improving (score: {brightness:.1f}) - continue current routine and consider brightening products")
        elif brightness > 75:
            insights.append(f"Beautiful skin glow detected (score: {brightness:.1f}) - your skincare and lifestyle choices are creating radiant skin!")
        
        # Wrinkles - Age-appropriate insights
        if wrinkles < 20:
            insights.append(f"Fine lines are quite visible (score: {wrinkles:.1f}) - consider retinol treatment, better moisturizing, and sun protection")
        elif wrinkles < 35:
            insights.append(f"Some fine lines detected (score: {wrinkles:.1f}) - maintain hydration, use anti-aging products, and protect from UV")
        elif wrinkles < 50:
            insights.append(f"Minimal aging signs (score: {wrinkles:.1f}) - maintain current routine and consider preventive treatments")
        elif wrinkles > 70:
            insights.append(f"Remarkably smooth skin (score: {wrinkles:.1f}) - your anti-aging routine is highly effective!")
        
        # Texture - Detailed analysis
        if texture < 25:
            insights.append(f"Skin texture appears rough (score: {texture:.1f}) - try gentle exfoliation, intensive moisturizing, and consult dermatologist")
        elif texture < 40:
            insights.append(f"Skin texture needs improvement (score: {texture:.1f}) - focus on hydration, gentle care, and consistent routine")
        elif texture < 55:
            insights.append(f"Skin texture is improving (score: {texture:.1f}) - continue gentle exfoliation and hydrating products")
        elif texture > 75:
            insights.append(f"Skin texture is beautifully smooth (score: {texture:.1f}) - your care routine is creating excellent results!")
        
        # Pore Size - Comprehensive assessment
        if pore_size < 25:
            insights.append(f"Pores appear enlarged (score: {pore_size:.1f}) - try salicylic acid, pore-minimizing treatments, and oil control")
        elif pore_size < 40:
            insights.append(f"Pores are somewhat visible (score: {pore_size:.1f}) - consider regular exfoliation, clay masks, and niacinamide")
        elif pore_size < 55:
            insights.append(f"Pore appearance is improving (score: {pore_size:.1f}) - maintain current routine and consider pore-refining products")
        elif pore_size > 70:
            insights.append(f"Pores look beautifully refined (score: {pore_size:.1f}) - your pore care routine is working excellently!")
        
        # Cross-feature pattern insights
        sleep_indicators = [dark_circles, puffiness, brightness]
        skin_indicators = [brightness, wrinkles, texture, pore_size]
        
        # Sleep pattern analysis
        if all(score < 40 for score in sleep_indicators):
            insights.append("Multiple indicators suggest poor sleep quality - prioritize sleep hygiene and stress management")
        elif all(score > 60 for score in sleep_indicators):
            insights.append("All sleep indicators are excellent - your rest and recovery routine is working perfectly!")
        
        # Skin health pattern analysis
        if all(score < 35 for score in skin_indicators):
            insights.append("Multiple skin concerns detected - consider comprehensive skincare routine overhaul")
        elif all(score > 65 for score in skin_indicators):
            insights.append("All skin health indicators are excellent - your skincare routine is highly effective!")
        
        # Lifestyle correlation insights
        sleep_hours = routine.get('sleep_hours', 0)
        water_intake = routine.get('water_intake', 0)
        
        if sleep_hours > 0 and dark_circles < 50:
            if sleep_hours < 6:
                insights.append(f"Your {sleep_hours}-hour sleep schedule is directly contributing to dark circles - aim for 7+ hours")
            elif sleep_hours < 7:
                insights.append(f"Increasing sleep from {sleep_hours} to 8 hours could improve dark circles by 30-50%")
        
        if water_intake > 0 and brightness < 50:
            if water_intake < 6:
                insights.append(f"Increasing water intake from {water_intake} to 8+ glasses could improve skin brightness significantly")
            elif water_intake < 8:
                insights.append(f"Your {water_intake}-glass water intake is good - increasing to 8+ glasses could enhance skin glow")
        
        return insights[:6]  # Limit to top 6 most relevant insights
    
    def _generate_dynamic_recommendations(self, features: Dict, routine: Dict, sleep_score: int, skin_score: int) -> List[str]:
        """Generate dynamic, personalized recommendations based on actual scores and patterns"""
        recommendations = []
        
        # Get feature scores
        dark_circles = features.get('dark_circles', 0)
        puffiness = features.get('puffiness', 0)
        brightness = features.get('brightness', 0)
        wrinkles = features.get('wrinkles', 0)
        texture = features.get('texture', 0)
        pore_size = features.get('pore_size', 0)
        
        # Prioritize recommendations based on worst scores
        feature_scores = {
            'dark_circles': dark_circles,
            'puffiness': puffiness,
            'brightness': brightness,
            'wrinkles': wrinkles,
            'texture': texture,
            'pore_size': pore_size
        }
        
        # Sort features by score (worst first)
        sorted_features = sorted(feature_scores.items(), key=lambda x: x[1])
        
        # Generate recommendations for top 3 worst features
        for feature_name, score in sorted_features[:3]:
            if feature_name == 'dark_circles' and score < 50:
                if score < 30:
                    recommendations.extend([
                        f"URGENT: Apply cold compress for 15 minutes to reduce severe dark circles (score: {score:.1f})",
                        "Use eye cream with caffeine or vitamin K twice daily",
                        "Prioritize 8+ hours of quality sleep tonight"
                    ])
                elif score < 45:
                    recommendations.extend([
                        f"Apply cold eye mask for 10 minutes (score: {score:.1f})",
                        "Use retinol eye cream at night (start slowly)",
                        "Sleep with head slightly elevated"
                    ])
                else:
                    recommendations.extend([
                        f"Use caffeine eye cream morning and night (score: {score:.1f})",
                        "Try cold spoon therapy for 5 minutes"
                    ])
            
            elif feature_name == 'puffiness' and score < 50:
                if score < 25:
                    recommendations.extend([
                        f"URGENT: Sleep with head elevated on extra pillows (score: {score:.1f})",
                        "Reduce sodium intake to under 2000mg daily",
                        "Apply cold cucumber slices for 10 minutes"
                    ])
                elif score < 40:
                    recommendations.extend([
                        f"Sleep with head slightly elevated (score: {score:.1f})",
                        "Reduce processed foods and increase water intake",
                        "Try lymphatic drainage massage"
                    ])
                else:
                    recommendations.extend([
                        f"Stay well hydrated throughout the day (score: {score:.1f})",
                        "Apply cool eye gel in the morning"
                    ])
            
            elif feature_name == 'brightness' and score < 50:
                if score < 30:
                    recommendations.extend([
                        f"URGENT: Increase water intake to 10+ glasses today (score: {score:.1f})",
                        "Apply vitamin C serum in the morning",
                        "Use hydrating face mask tonight"
                    ])
                elif score < 45:
                    recommendations.extend([
                        f"Use brightening serum with vitamin C (score: {score:.1f})",
                        "Try gentle exfoliation 2-3 times this week",
                        "Apply hydrating toner before moisturizer"
                    ])
                else:
                    recommendations.extend([
                        f"Use vitamin C serum for skin radiance (score: {score:.1f})",
                        "Apply moisturizer while skin is still damp"
                    ])
            
            elif feature_name == 'wrinkles' and score < 50:
                if score < 25:
                    recommendations.extend([
                        f"URGENT: Start retinol treatment tonight (score: {score:.1f})",
                        "Apply intensive moisturizer with peptides",
                        "Use sunscreen religiously to prevent further damage"
                    ])
                elif score < 40:
                    recommendations.extend([
                        f"Use anti-aging serum with retinol (score: {score:.1f})",
                        "Apply hyaluronic acid for intense hydration",
                        "Consider professional treatments"
                    ])
                else:
                    recommendations.extend([
                        f"Use peptide-rich moisturizer (score: {score:.1f})",
                        "Apply eye cream with retinol at night"
                    ])
            
            elif feature_name == 'texture' and score < 50:
                if score < 30:
                    recommendations.extend([
                        f"URGENT: Use gentle exfoliating mask tonight (score: {score:.1f})",
                        "Apply intensive moisturizer with ceramides",
                        "Consider professional microdermabrasion"
                    ])
                elif score < 45:
                    recommendations.extend([
                        f"Gentle exfoliation 2-3 times this week (score: {score:.1f})",
                        "Use hyaluronic acid serum for smoothness",
                        "Apply hydrating face mask 2x weekly"
                    ])
                else:
                    recommendations.extend([
                        f"Use gentle AHA exfoliant (score: {score:.1f})",
                        "Apply hydrating serum before moisturizer"
                    ])
            
            elif feature_name == 'pore_size' and score < 50:
                if score < 30:
                    recommendations.extend([
                        f"URGENT: Apply clay mask tonight to minimize pores (score: {score:.1f})",
                        "Use salicylic acid cleanser twice daily",
                        "Apply niacinamide serum for pore control"
                    ])
                elif score < 45:
                    recommendations.extend([
                        f"Use pore-minimizing toner with BHA (score: {score:.1f})",
                        "Apply niacinamide serum twice daily",
                        "Try weekly clay mask treatments"
                    ])
                else:
                    recommendations.extend([
                        f"Use salicylic acid cleanser (score: {score:.1f})",
                        "Apply pore-refining serum"
                    ])
        
        # Add lifestyle-based recommendations
        sleep_hours = routine.get('sleep_hours', 0)
        water_intake = routine.get('water_intake', 0)
        
        if sleep_hours > 0 and sleep_score < 60:
            if sleep_hours < 6:
                recommendations.append(f"CRITICAL: Increase sleep from {sleep_hours} to 8+ hours - this will improve all skin metrics")
            elif sleep_hours < 7:
                recommendations.append(f"Extend sleep from {sleep_hours} to 8 hours for optimal skin recovery")
        
        if water_intake > 0 and skin_score < 60:
            if water_intake < 6:
                recommendations.append(f"INCREASE: Water intake from {water_intake} to 8+ glasses daily for better skin hydration")
            elif water_intake < 8:
                recommendations.append(f"Boost water intake from {water_intake} to 8+ glasses for optimal skin plumpness")
        
        # Add skincare product recommendations based on detected products
        skincare_products = routine.get('skincare_products', [])
        detected_products = set()
        
        if skincare_products:
            for product_id in skincare_products:
                product_lower = product_id.lower()
                if 'vitamin_c' in product_lower:
                    detected_products.add('vitamin_c')
                elif 'retinol' in product_lower:
                    detected_products.add('retinol')
                elif 'sunscreen' in product_lower:
                    detected_products.add('sunscreen')
        
        # Suggest missing products based on skin concerns
        if brightness < 50 and 'vitamin_c' not in detected_products:
            recommendations.append("ADD: Vitamin C serum for skin brightening and collagen production")
        if wrinkles < 50 and 'retinol' not in detected_products:
            recommendations.append("CONSIDER: Retinol treatment for anti-aging and texture improvement")
        if not detected_products or 'sunscreen' not in detected_products:
            recommendations.append("ESSENTIAL: Daily sunscreen (SPF 30+) to prevent further skin damage")
        
        return recommendations[:8]  # Limit to top 8 most relevant recommendations

class RuleBasedProvider(BaseLLMProvider):
    """Free rule-based provider - always available"""
    
    def is_available(self) -> bool:
        return True
    
    async def generate_summary(self, context: str, analysis_data: Dict) -> Dict[str, Any]:
        """Generate summary using rule-based logic"""
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        features = analysis_data.get('features', {})
        routine = analysis_data.get('routine', {})
        
        # Generate personalized daily summary with proper health scoring
        if sleep_score < 30 and skin_score < 30:
            daily_summary = f"Your Sleep Score is {sleep_score} and Skin Health Score is {skin_score}. Both scores indicate areas needing attention. Focus on immediate improvements: prioritize 8+ hours of sleep, increase water intake to 8+ glasses, and establish a basic skincare routine."
        elif sleep_score < 50 or skin_score < 50:
            daily_summary = f"Your Sleep Score is {sleep_score} and Skin Health Score is {skin_score}. These scores suggest room for improvement. Let's optimize: aim for 7-8 hours of sleep, drink 6-8 glasses of water, and consider adding targeted skincare products."
        elif sleep_score < 75 or skin_score < 75:
            daily_summary = f"Your Sleep Score is {sleep_score} and Skin Health Score is {skin_score}. Good progress! Continue focusing on consistent sleep and skincare routines for optimal health."
        else:
            daily_summary = f"Excellent! Your Sleep Score is {sleep_score} and Skin Health Score is {skin_score}. You're maintaining great health - keep up your current routine and consider adding advanced products for further improvement."
        
        # Generate dynamic, personalized insights based on actual feature scores
        insights = self._generate_dynamic_insights(features, routine)
        
        # Add comprehensive routine-based insights
        if routine.get('sleep_hours'):
            sleep_hours = routine['sleep_hours']
            if sleep_hours < 5:
                insights.append(f"Critical sleep deficiency ({sleep_hours}h) - this severely impacts skin repair and dark circles")
            elif sleep_hours < 6:
                insights.append(f"Insufficient sleep ({sleep_hours}h) - aim for 7-9 hours for optimal skin health")
            elif sleep_hours < 7:
                insights.append(f"Adequate sleep ({sleep_hours}h) - consider 7-8 hours for better skin recovery")
            elif sleep_hours >= 8:
                insights.append(f"Excellent sleep routine ({sleep_hours}h) - this supports healthy skin and reduces puffiness")
        
        if routine.get('water_intake'):
            water_intake = routine['water_intake']
            if water_intake < 4:
                insights.append(f"Severe dehydration ({water_intake} glasses) - this causes dull, dry skin and accentuates wrinkles")
            elif water_intake < 6:
                insights.append(f"Moderate hydration ({water_intake} glasses) - increase to 8+ glasses for plumper, healthier skin")
            elif water_intake >= 8:
                insights.append(f"Excellent hydration ({water_intake} glasses) - well-hydrated skin appears smooth and glowing")
        
        # Skincare routine insights
        skincare_products = routine.get('skincare_products', [])
        product_used_text = routine.get('product_used', '')
        
        if skincare_products or product_used_text:
            skincare_insights = []
            detected_products = set()
            
            # Process new skincare_products array
            if skincare_products:
                for product_id in skincare_products:
                    product_lower = product_id.lower()
                    if 'vitamin_c' in product_lower or 'vitamin c' in product_lower:
                        detected_products.add('vitamin_c')
                    elif 'retinol' in product_lower:
                        detected_products.add('retinol')
                    elif 'sunscreen' in product_lower:
                        detected_products.add('sunscreen')
                    elif 'moisturizer' in product_lower:
                        detected_products.add('moisturizer')
                    elif 'hyaluronic' in product_lower:
                        detected_products.add('hyaluronic')
                    elif 'niacinamide' in product_lower:
                        detected_products.add('niacinamide')
                    elif 'peptide' in product_lower:
                        detected_products.add('peptide')
                    elif 'aha' in product_lower or 'alpha_hydroxy' in product_lower:
                        detected_products.add('aha')
                    elif 'bha' in product_lower or 'beta_hydroxy' in product_lower:
                        detected_products.add('bha')
                    elif 'azelaic' in product_lower:
                        detected_products.add('azelaic')
                    elif 'cleanser' in product_lower:
                        detected_products.add('cleanser')
                    elif 'toner' in product_lower:
                        detected_products.add('toner')
                    elif 'mask' in product_lower:
                        detected_products.add('mask')
                    elif 'exfoliant' in product_lower:
                        detected_products.add('exfoliant')
            
            # Process legacy product_used text
            if product_used_text:
                products_lower = product_used_text.lower()
                if 'vitamin c' in products_lower:
                    detected_products.add('vitamin_c')
                if 'retinol' in products_lower:
                    detected_products.add('retinol')
                if 'sunscreen' in products_lower:
                    detected_products.add('sunscreen')
                if 'moisturizer' in products_lower:
                    detected_products.add('moisturizer')
                if 'serum' in products_lower:
                    detected_products.add('serum')
            
            # Generate insights based on detected products
            if 'vitamin_c' in detected_products:
                skincare_insights.append("Vitamin C detected - great for brightening and collagen production")
            if 'retinol' in detected_products:
                skincare_insights.append("Retinol detected - excellent for anti-aging and texture improvement")
            if 'sunscreen' in detected_products:
                skincare_insights.append("Sunscreen detected - crucial for preventing UV damage and premature aging")
            if 'moisturizer' in detected_products:
                skincare_insights.append("Moisturizer detected - essential for maintaining skin barrier function")
            if 'hyaluronic' in detected_products:
                skincare_insights.append("Hyaluronic Acid detected - excellent for intense hydration and plumping")
            if 'niacinamide' in detected_products:
                skincare_insights.append("Niacinamide detected - great for pore control and oil regulation")
            if 'peptide' in detected_products:
                skincare_insights.append("Peptides detected - excellent for anti-aging and skin firmness")
            if 'aha' in detected_products:
                skincare_insights.append("AHA detected - gentle exfoliation for brighter, smoother skin")
            if 'bha' in detected_products:
                skincare_insights.append("BHA detected - effective for pore cleansing and acne treatment")
            if 'azelaic' in detected_products:
                skincare_insights.append("Azelaic Acid detected - great for anti-inflammatory and hyperpigmentation treatment")
            if 'cleanser' in detected_products:
                skincare_insights.append("Cleanser detected - good foundation for skin care routine")
            if 'toner' in detected_products:
                skincare_insights.append("Toner detected - helps balance pH and prep skin for other products")
            if 'mask' in detected_products:
                skincare_insights.append("Face mask detected - intensive treatment for enhanced skin health")
            if 'exfoliant' in detected_products:
                skincare_insights.append("Exfoliant detected - helps improve skin texture and cell turnover")
            
            if skincare_insights:
                insights.extend(skincare_insights)
            else:
                insights.append("Basic skincare products detected - consider adding targeted treatments for better results")
        else:
            insights.append("No skincare routine specified - basic routine (cleanser, moisturizer, sunscreen) would help")
        
        # Daily note insights
        if routine.get('daily_note'):
            daily_note = routine['daily_note'].lower()
            if any(word in daily_note for word in ['stress', 'stressed', 'anxious', 'worried']):
                insights.append("Stress detected in notes - stress hormones can worsen skin conditions and dark circles")
            if any(word in daily_note for word in ['tired', 'exhausted', 'fatigue']):
                insights.append("Fatigue mentioned - this correlates with poor sleep quality and skin appearance")
            if any(word in daily_note for word in ['happy', 'good', 'great', 'excellent']):
                insights.append("Positive mood noted - good mental health supports overall skin health")
        
        # Generate recommendations
        # Generate dynamic, personalized recommendations
        recommendations = self._generate_dynamic_recommendations(features, routine, sleep_score, skin_score)
        
        # Comprehensive lifestyle-based recommendations
        if routine.get('sleep_hours'):
            sleep_hours = routine['sleep_hours']
            if sleep_hours < 6:
                recommendations.extend([
                    f"Prioritize sleep - aim for 7-9 hours (currently {sleep_hours}h)",
                    "Create a consistent bedtime routine",
                    "Avoid screens 1 hour before bed",
                    "Consider sleep tracking to monitor patterns"
                ])
            elif sleep_hours < 8:
                recommendations.append(f"Good sleep foundation ({sleep_hours}h) - consider extending to 8 hours for optimal skin repair")
        
        if routine.get('water_intake'):
            water_intake = routine['water_intake']
            if water_intake < 6:
                recommendations.extend([
                    f"Increase water intake to 8+ glasses daily (currently {water_intake})",
                    "Set hourly water reminders",
                    "Add lemon or cucumber for flavor",
                    "Monitor urine color - should be pale yellow"
                ])
            elif water_intake < 8:
                recommendations.append(f"Good hydration progress ({water_intake} glasses) - aim for 8+ for optimal skin plumpness")
        
        # Skincare routine recommendations
        skincare_products = routine.get('skincare_products', [])
        product_used_text = routine.get('product_used', '')
        
        if skincare_products or product_used_text:
            detected_products = set()
            
            # Process new skincare_products array
            if skincare_products:
                for product_id in skincare_products:
                    product_lower = product_id.lower()
                    if 'vitamin_c' in product_lower or 'vitamin c' in product_lower:
                        detected_products.add('vitamin_c')
                    elif 'retinol' in product_lower:
                        detected_products.add('retinol')
                    elif 'sunscreen' in product_lower:
                        detected_products.add('sunscreen')
                    elif 'moisturizer' in product_lower:
                        detected_products.add('moisturizer')
                    elif 'hyaluronic' in product_lower:
                        detected_products.add('hyaluronic')
                    elif 'niacinamide' in product_lower:
                        detected_products.add('niacinamide')
                    elif 'peptide' in product_lower:
                        detected_products.add('peptide')
                    elif 'aha' in product_lower or 'alpha_hydroxy' in product_lower:
                        detected_products.add('aha')
                    elif 'bha' in product_lower or 'beta_hydroxy' in product_lower:
                        detected_products.add('bha')
                    elif 'azelaic' in product_lower:
                        detected_products.add('azelaic')
                    elif 'cleanser' in product_lower:
                        detected_products.add('cleanser')
                    elif 'toner' in product_lower:
                        detected_products.add('toner')
                    elif 'mask' in product_lower:
                        detected_products.add('mask')
                    elif 'exfoliant' in product_lower:
                        detected_products.add('exfoliant')
            
            # Process legacy product_used text
            if product_used_text:
                products_lower = product_used_text.lower()
                if 'vitamin c' in products_lower:
                    detected_products.add('vitamin_c')
                if 'retinol' in products_lower:
                    detected_products.add('retinol')
                if 'sunscreen' in products_lower:
                    detected_products.add('sunscreen')
                if 'moisturizer' in products_lower:
                    detected_products.add('moisturizer')
                if 'serum' in products_lower:
                    detected_products.add('serum')
            
            # Generate recommendations based on detected products and skin concerns
            if 'vitamin_c' in detected_products and skin_score >= 70:
                recommendations.append("Your Vitamin C routine is working well - keep it up!")
            elif 'retinol' in detected_products and skin_score >= 75:
                recommendations.append("Retinol is showing great results - continue consistently")
            elif 'sunscreen' in detected_products and skin_score >= 65:
                recommendations.append("Sunscreen protection is paying off - maintain daily use")
            elif 'hyaluronic' in detected_products and skin_score >= 70:
                recommendations.append("Hyaluronic Acid is providing excellent hydration - continue use")
            elif 'niacinamide' in detected_products and skin_score >= 70:
                recommendations.append("Niacinamide is helping with pore control - keep using it")
            else:
                # Suggest missing products based on skin concerns
                if features.get('brightness', 0) < -20 and 'vitamin_c' not in detected_products:
                    recommendations.append("Consider adding Vitamin C serum for brightness")
                if features.get('wrinkles', 0) < -20 and 'retinol' not in detected_products:
                    recommendations.append("Consider adding retinol for anti-aging")
                if features.get('texture', 0) < -20 and 'aha' not in detected_products:
                    recommendations.append("Consider adding AHA exfoliant for texture improvement")
                if features.get('puffiness', 0) < -20 and 'niacinamide' not in detected_products:
                    recommendations.append("Consider adding niacinamide for pore control and inflammation")
                if 'sunscreen' not in detected_products:
                    recommendations.append("Add daily sunscreen - essential for preventing UV damage")
                if 'cleanser' not in detected_products:
                    recommendations.append("Add a gentle cleanser to your routine")
                if 'moisturizer' not in detected_products:
                    recommendations.append("Add a moisturizer to maintain skin barrier function")
        else:
            recommendations.extend([
                "Establish a basic skincare routine",
                "Start with: cleanser, moisturizer, sunscreen",
                "Consider adding targeted treatments based on concerns"
            ])
        
        # Daily note-based recommendations
        if routine.get('daily_note'):
            daily_note = routine['daily_note'].lower()
            if any(word in daily_note for word in ['stress', 'stressed', 'anxious']):
                recommendations.extend([
                    "Practice stress management techniques",
                    "Try meditation or deep breathing",
                    "Consider yoga or gentle exercise",
                    "Ensure adequate sleep to manage stress"
                ])
            if any(word in daily_note for word in ['tired', 'exhausted']):
                recommendations.extend([
                    "Prioritize rest and recovery",
                    "Check sleep quality and duration",
                    "Consider power naps (20-30 minutes)",
                    "Evaluate caffeine intake timing"
                ])
        
        # Add safety disclaimer to recommendations
        if recommendations:
            recommendations.append("⚠️ Always consult a dermatologist before trying new skincare procedures or products")
        
        # Add risk assessment and progress tracking for rule-based provider
        risk_assessment = []
        if sleep_score < 30 or skin_score < 30:
            risk_assessment.append("HIGH RISK: Critical scores indicate immediate attention needed")
        elif sleep_score < 50 or skin_score < 50:
            risk_assessment.append("MODERATE RISK: Suboptimal scores suggest lifestyle improvements needed")
        else:
            risk_assessment.append("LOW RISK: Good scores - maintain current healthy habits")
        
        progress_tracking = [
            "Week 1: Focus on sleep consistency and basic skincare routine",
            "Week 2: Monitor hydration and track sleep quality improvements",
            "Month 1: Evaluate overall progress and adjust routine as needed"
        ]
        
        return {
            "daily_summary": daily_summary,
            "key_insights": insights[:7],  # Up to 7 insights
            "recommendations": recommendations[:7],  # Up to 7 recommendations
            "risk_assessment": risk_assessment[:5],  # Up to 5 risk factors
            "progress_tracking": progress_tracking[:5],  # Up to 5 tracking items
            "confidence_score": 8,  # High confidence for rule-based
            "validated": True  # Rule-based is always validated
        }

class HuggingFaceFreeProvider(BaseLLMProvider):
    """Free Hugging Face Inference API provider"""
    
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        self.headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"}
    
    def is_available(self) -> bool:
        return bool(os.getenv('HUGGINGFACE_API_KEY'))
    
    async def generate_summary(self, context: str, analysis_data: Dict) -> Dict[str, Any]:
        """Generate summary using Hugging Face free API with world-class prompt"""
        try:
            import httpx
            
            # Use the world-class prompt
            prompt = self._create_world_class_prompt(context, analysis_data)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    headers=self.headers,
                    json={"inputs": prompt},
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    # Parse the response and return structured data
                    return self._parse_huggingface_response(result)
                else:
                    raise Exception(f"API error: {response.status_code}")
                    
        except Exception as e:
            print(f"HuggingFace API error: {e}")
            # Fallback to rule-based
            rule_provider = RuleBasedProvider()
            return await rule_provider.generate_summary(context, analysis_data)
    
    def _parse_huggingface_response(self, response: Any) -> Dict[str, Any]:
        """Parse Hugging Face response with advanced format handling"""
        try:
            # Try to extract text from HuggingFace response
            if isinstance(response, list) and len(response) > 0:
                response_text = response[0].get('generated_text', '')
            elif isinstance(response, dict):
                response_text = response.get('generated_text', '')
            else:
                response_text = str(response)
            
            # Use the same advanced parsing as Ollama
            return self._parse_ollama_response(response_text)
            
        except Exception as e:
            print(f"HuggingFace parsing error: {e}")
            # Fallback to basic format
            return {
                "daily_summary": "Analysis completed using AI insights",
                "key_insights": ["AI-powered analysis completed"],
                "recommendations": ["Follow personalized recommendations above"],
                "risk_assessment": ["Continue monitoring for any health concerns"],
                "progress_tracking": ["Track your progress weekly for best results"],
                "confidence_score": 5,
                "validated": False
            }

class OllamaLocalProvider(BaseLLMProvider):
    """Local Ollama provider - completely free and private"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "tinyllama"  # Fast and efficient model for real-time analysis
    
    def is_available(self) -> bool:
        try:
            import httpx
            # Check if Ollama is running locally (synchronous check)
            with httpx.Client() as client:
                response = client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except:
            return False
    
    async def _check_ollama(self) -> bool:
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except:
            return False
    
    async def generate_summary(self, context: str, analysis_data: Dict) -> Dict[str, Any]:
        """Generate summary using local Ollama with world-class prompt"""
        try:
            import httpx
            
            # Use the world-class prompt
            prompt = self._create_world_class_prompt(context, analysis_data)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return self._parse_ollama_response(result.get('response', ''))
                else:
                    raise Exception(f"Ollama error: {response.status_code}")
                    
        except Exception as e:
            print(f"Ollama error: {e}")
            # Fallback to rule-based
            rule_provider = RuleBasedProvider()
            return await rule_provider.generate_summary(context, analysis_data)
    
    def _parse_ollama_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Ollama response with world-class format handling"""
        lines = response_text.split('\n')
        
        daily_summary = ""
        key_insights = []
        recommendations = []
        risk_assessment = []
        progress_tracking = []
        confidence_score = 0
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for world-class section headers
            if "daily summary:" in line.lower():
                current_section = "summary"
                summary_text = line.split(':', 1)[1].strip()
                if summary_text:
                    daily_summary = summary_text
            elif "advanced insights:" in line.lower() or "key insights:" in line.lower():
                current_section = "insights"
            elif "strategic recommendations:" in line.lower() or "recommendations:" in line.lower():
                current_section = "recommendations"
            elif "risk assessment:" in line.lower():
                current_section = "risks"
            elif "progress tracking protocol:" in line.lower() or "progress tracking:" in line.lower():
                current_section = "progress"
            elif "confidence assessment:" in line.lower() or "confidence score:" in line.lower():
                # Extract confidence score
                try:
                    confidence_text = line.split(':', 1)[1].strip()
                    confidence_score = float(confidence_text.split('/')[0])
                except:
                    confidence_score = 5  # Default moderate confidence
            elif "daily summary" in line.lower() or "summary" in line.lower():
                current_section = "summary"
            elif "insights" in line.lower():
                current_section = "insights"
            elif "recommendations" in line.lower() or "advice" in line.lower():
                current_section = "recommendations"
            elif "risk" in line.lower():
                current_section = "risks"
            elif "progress" in line.lower() or "tracking" in line.lower():
                current_section = "progress"
            # Handle world-class bullet points and numbered lists
            elif line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '-', '•', 'Priority', 'Primary Finding', 'Correlation Analysis', 'Trend Prediction', 'Risk Assessment', 'Optimization Opportunity')):
                clean_line = line.lstrip('1234567.-•PriorityPrimaryFindingCorrelationAnalysisTrendPredictionRiskAssessmentOptimizationOpportunity ').strip()
                if current_section == "insights":
                    key_insights.append(clean_line)
                elif current_section == "recommendations":
                    recommendations.append(clean_line)
                elif current_section == "risks":
                    risk_assessment.append(clean_line)
                elif current_section == "progress":
                    progress_tracking.append(clean_line)
            # Handle summary text
            elif current_section == "summary" and not daily_summary:
                daily_summary = line
            # Handle risk assessment text
            elif current_section == "risks" and ("high risk" in line.lower() or "moderate risk" in line.lower() or "low risk" in line.lower()):
                risk_assessment.append(line)
            # Handle progress tracking text
            elif current_section == "progress" and ("week" in line.lower() or "month" in line.lower() or "day" in line.lower() or "metrics" in line.lower() or "expectations" in line.lower() or "goals" in line.lower()):
                progress_tracking.append(line)
        
        # Fallback if parsing failed
        if not daily_summary:
            daily_summary = "Your analysis shows areas for improvement. Focus on getting better sleep and maintaining a consistent skincare routine."
        
        if not key_insights:
            key_insights = ["Analysis completed - check recommendations for next steps"]
        
        if not recommendations:
            recommendations = ["Get 7-9 hours of sleep", "Stay hydrated", "Use gentle skincare products"]
        
        if not risk_assessment:
            risk_assessment = ["Continue monitoring for any health concerns"]
        
        if not progress_tracking:
            progress_tracking = ["Track your progress weekly for best results"]
        
        # Enhanced return with all new fields
        return {
            "daily_summary": daily_summary,
            "key_insights": key_insights[:7],  # Up to 7 insights
            "recommendations": recommendations[:7],  # Up to 7 recommendations
            "risk_assessment": risk_assessment[:5],  # Up to 5 risk factors
            "progress_tracking": progress_tracking[:5],  # Up to 5 tracking items
            "confidence_score": confidence_score,
            "validated": confidence_score >= 6  # Mark as validated if confidence is high
        }

class GrokProvider(BaseLLMProvider):
    """Grok API provider - xAI's Grok model"""
    
    def __init__(self):
        self.api_key = os.getenv('XAI_API_KEY')  # xAI API key
        self.model = "grok-beta"  # Correct Grok model name
    
    def is_available(self) -> bool:
        return self.api_key is not None
    
    async def generate_summary(self, context: str, analysis_data: Dict) -> Dict[str, Any]:
        """Generate summary using Grok API - xAI's model - TOKEN OPTIMIZED"""
        try:
            import httpx
            
            # Use the ultra-concise prompt to minimize tokens (2-liner format)
            prompt = self._create_concise_prompt(context, analysis_data)
            
            async with httpx.AsyncClient(timeout=2.0) as client:  # 2 second timeout for speed
                response = await client.post(
                    "https://api.x.ai/v1/chat/completions",  # xAI API endpoint
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "Concise skincare advisor. 2 lines max."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 80,  # Reduced to 80 for SPEED (2 short lines only)
                        "temperature": 0.2  # Lower for faster, focused responses
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content'].strip()
                    
                    # Parse 2-liner response (same format as OpenAI)
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    daily_summary = lines[0] if len(lines) > 0 else "Analysis complete."
                    recommendation = lines[1] if len(lines) > 1 else "Continue your routine."
                    
                    return {
                        "daily_summary": daily_summary,
                        "key_insights": [daily_summary],
                        "recommendations": [recommendation],
                        "model": "Grok (xAI)",
                        "provider": "xai",
                        "tokens_used": result.get('usage', {}).get('total_tokens', 0)
                    }
                else:
                    print(f"Grok API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"Grok error: {e}")
            return None
    
    def _parse_grok_response(self, content: str, analysis_data: Dict) -> Dict[str, Any]:
        """Parse Grok response and format it consistently with other providers"""
        try:
            # Use Grok's response as the daily summary
            daily_summary = content.strip()
            
            # Extract insights from Grok's response
            insights = []
            recommendations = []
            
            # Parse the response for improvement areas and suggestions
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line and ('improvement' in line.lower() or 'needs work' in line.lower() or 'focus' in line.lower()):
                    insights.append(line)
                elif line and ('recommend' in line.lower() or 'try' in line.lower() or 'use' in line.lower() or 'product' in line.lower()):
                    recommendations.append(line)
            
            # If no insights found, generate based on scores
            if not insights:
                features = analysis_data.get('features', {})
                sleep_score = analysis_data.get('sleep_score', 0)
                skin_score = analysis_data.get('skin_health_score', 0)
                
                # Focus on areas that need improvement
                if features.get('dark_circles', 0) < 50:
                    insights.append("Dark circles need attention - improve sleep quality")
                if features.get('brightness', 0) < 50:
                    insights.append("Skin brightness can be improved with vitamin C")
                if features.get('wrinkles', 0) < 50:
                    insights.append("Fine lines visible - consider retinol treatment")
                if features.get('texture', 0) < 50:
                    insights.append("Skin texture needs smoothing - try gentle exfoliation")
                if features.get('pore_size', 0) < 50:
                    insights.append("Pores appear enlarged - use salicylic acid")
                if sleep_score < 50:
                    insights.append("Sleep quality affecting skin health")
                if skin_score < 50:
                    insights.append("Overall skin health needs improvement")
            
            # If no recommendations found, add basic ones
            if not recommendations:
                recommendations = [
                    "Use vitamin C serum for brightness",
                    "Apply retinol at night for anti-aging",
                    "Get 7-8 hours of quality sleep",
                    "Use gentle cleanser and moisturizer daily",
                    "Apply sunscreen every morning"
                ]
            
            return {
                "daily_summary": daily_summary,
                "key_insights": insights[:5],
                "recommendations": recommendations[:5],
                "risk_assessment": ["Monitor progress weekly"],
                "progress_tracking": ["Track improvements in 1-2 weeks"],
                "confidence_score": 8,
                "validated": True,
                "model": "Grok (xAI)",
                "provider": "xai"
            }
            
        except Exception as e:
            print(f"Error parsing Grok response: {e}")
            # Fallback to basic format
            return {
                "daily_summary": content,
                "key_insights": ["AI analysis completed"],
                "recommendations": ["Follow personalized recommendations"],
                "risk_assessment": ["Continue monitoring health"],
                "progress_tracking": ["Track progress weekly"],
                "confidence_score": 5,
                "validated": False,
                "model": "Grok (xAI)",
                "provider": "xai"
            }

class OpenAIFreeProvider(BaseLLMProvider):
    """OpenAI API provider - fastest and most accurate"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-4o-mini"  # CHEAPEST! Real model name
    
    def is_available(self) -> bool:
        return self.api_key is not None
    
    async def generate_summary(self, context: str, analysis_data: Dict) -> Dict[str, Any]:
        """Generate summary using OpenAI API - TOKEN OPTIMIZED for cost efficiency"""
        try:
            import httpx
            
            # Use the ultra-concise prompt to minimize tokens (2-liner format)
            prompt = self._create_concise_prompt(context, analysis_data)
            
            async with httpx.AsyncClient(timeout=2.0) as client:  # 2 second timeout for speed
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "Concise skincare advisor. 2 lines max."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 80,  # Reduced to 80 for SPEED (2 short lines only)
                        "temperature": 0.2  # Lower for faster, focused responses
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content'].strip()
                    
                    # Parse 2-liner response
                    lines = [line.strip() for line in content.split('\n') if line.strip()]
                    daily_summary = lines[0] if len(lines) > 0 else "Analysis complete."
                    recommendation = lines[1] if len(lines) > 1 else "Continue your routine."
                    
                    return {
                        "daily_summary": daily_summary,
                        "key_insights": [daily_summary],
                        "recommendations": [recommendation],
                        "model": "OpenAI GPT-5 Nano",
                        "provider": "openai",
                        "tokens_used": result.get('usage', {}).get('total_tokens', 0)
                    }
                else:
                    print(f"OpenAI API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            print(f"OpenAI error: {e}")
            return None

class FlexibleLLMService:
    """Main service that manages different LLM providers"""
    
    def __init__(self):
        self.providers = {
            ModelType.RULE_BASED: RuleBasedProvider(),
            ModelType.HUGGINGFACE_FREE: HuggingFaceFreeProvider(),
            ModelType.OLLAMA_LOCAL: OllamaLocalProvider(),
            ModelType.OPENAI_FREE: OpenAIFreeProvider(),
            ModelType.GROK: GrokProvider(),  # Add Grok for speed
        }
        
        # Default model priority (try in order) - OPTIMIZED FOR ACCURACY & SPEED
        self.model_priority = [
            ModelType.OPENAI_FREE,       # Primary: GPT-5 Nano - ACCURACY + token-optimized for speed
            ModelType.GROK,              # Backup: Grok (xAI)
            ModelType.RULE_BASED,        # Fallback: Instant
            ModelType.HUGGINGFACE_FREE,  # Backup: Free API
            ModelType.OLLAMA_LOCAL,      # Last resort: Slow local model
        ]
        
        # Add advanced insights engine
        self.insights_engine = AdvancedInsightsEngine()
    
    def get_available_models(self) -> List[ModelType]:
        """Get list of available models"""
        available = []
        for model_type, provider in self.providers.items():
            if provider.is_available():
                available.append(model_type)
        return available
    
    def set_model_priority(self, priority: List[ModelType]):
        """Set the priority order for model selection"""
        self.model_priority = priority
    
    async def generate_smart_summary(self, analysis_data: Dict, routine_data: Optional[Dict] = None, historical_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Generate smart summary using the best available model with trend analysis"""
        
        # Create context with trend analysis if historical data is available
        context = self._create_analysis_context(analysis_data, routine_data, historical_data)
        
        # Try models in priority order
        for model_type in self.model_priority:
            if model_type in self.providers:
                provider = self.providers[model_type]
                if provider.is_available():
                    try:
                        print(f"🧠 Using {model_type.value} for smart summary generation")
                        result = await provider.generate_summary(context, analysis_data)
                        # Check if result is valid (not None)
                        if result is not None:
                            print(f"✅ Smart summary generated using {model_type.value}")
                            return result
                        else:
                            print(f"⚠️ {model_type.value} returned None, trying next provider")
                            continue
                    except Exception as e:
                        print(f"❌ {model_type.value} failed: {e}")
                        continue
        
        # If all models fail, use rule-based as final fallback
        print("⚠️ All models failed, using rule-based fallback")
        rule_provider = RuleBasedProvider()
        return await rule_provider.generate_summary(context, analysis_data)
    
    async def generate_daily_summary_with_insights(self, analysis_data: Dict, routine_data: Optional[Dict] = None, historical_data: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """Generate daily summary focused on current selfie + actionable recommendations, with historical insights"""
        
        # Generate daily summary (current selfie + immediate recommendations)
        daily_summary = await self.generate_smart_summary(analysis_data, routine_data, None)
        
        # Generate historical insights if data is available
        historical_insights = []
        if historical_data and len(historical_data) > 1 and feature_correlation_analyzer:
            try:
                # Get smart analysis for historical insights
                smart_analysis = feature_correlation_analyzer.analyze_feature_product_correlations(historical_data)
                
                if not smart_analysis.get('insufficient_data', True):
                    # Add historical insights to the daily summary
                    historical_insights = self._format_smart_insights(smart_analysis)
                    
                    # Add historical insights to key_insights
                    if 'key_insights' not in daily_summary:
                        daily_summary['key_insights'] = []
                    
                    # Add historical insights at the beginning
                    daily_summary['key_insights'] = historical_insights + daily_summary['key_insights']
                    
                    print(f"✅ Added {len(historical_insights)} historical insights to daily summary")
            except Exception as e:
                print(f"⚠️ Failed to generate historical insights: {e}")
        elif not feature_correlation_analyzer:
            print("⚠️ Feature correlation analyzer not available")
        
        return daily_summary
    
    def _create_analysis_context(self, analysis_data: Dict, routine_data: Optional[Dict] = None, historical_data: Optional[List[Dict]] = None) -> str:
        """Create enhanced context string for LLM with advanced lifestyle analysis and correlations"""
        # Use the dynamic context system for world-class analysis
        return self._create_dynamic_context(analysis_data, routine_data, historical_data)
    
    def _analyze_trends(self, historical_data: List[Dict], current_analysis: Dict) -> str:
        """Analyze trends from historical data"""
        if len(historical_data) < 3:
            return "Insufficient historical data for trend analysis"
        
        # Sort by date
        sorted_data = sorted(historical_data, key=lambda x: x.get('date', ''))
        
        # Calculate trends
        recent_data = sorted_data[-3:]  # Last 3 entries
        earlier_data = sorted_data[:3]  # First 3 entries
        
        recent_skin_avg = sum(entry.get('skin_health_score', 0) for entry in recent_data) / len(recent_data)
        earlier_skin_avg = sum(entry.get('skin_health_score', 0) for entry in earlier_data) / len(earlier_data)
        skin_improvement = recent_skin_avg - earlier_skin_avg
        
        recent_sleep_avg = sum(entry.get('sleep_score', 0) for entry in recent_data) / len(recent_data)
        earlier_sleep_avg = sum(entry.get('sleep_score', 0) for entry in earlier_data) / len(earlier_data)
        sleep_improvement = recent_sleep_avg - earlier_sleep_avg
        
        # Analyze product usage patterns
        product_usage = {}
        for entry in sorted_data:
            routine = entry.get('routine', {})
            products = routine.get('skincare_products', [])
            if routine.get('product_used'):
                products.extend(routine.get('product_used', '').split(', '))
            
            for product in products:
                if product not in product_usage:
                    product_usage[product] = []
                product_usage[product].append(entry.get('skin_health_score', 0))
        
        # Generate trend insights
        trend_insights = []
        
        if skin_improvement > 5:
            trend_insights.append(f"Your skin health has improved by {skin_improvement:.1f} points over time - great progress!")
        elif skin_improvement < -5:
            trend_insights.append(f"Your skin health has declined by {abs(skin_improvement):.1f} points - consider adjusting your routine")
        else:
            trend_insights.append("Your skin health has been stable - consider adding new products for further improvement")
        
        if sleep_improvement > 5:
            trend_insights.append(f"Your sleep quality has improved by {sleep_improvement:.1f} points - keep it up!")
        elif sleep_improvement < -5:
            trend_insights.append(f"Your sleep quality has declined by {abs(sleep_improvement):.1f} points - focus on better sleep habits")
        
        # Analyze product effectiveness
        for product, scores in product_usage.items():
            if len(scores) >= 3:
                early_avg = sum(scores[:len(scores)//2]) / (len(scores)//2)
                recent_avg = sum(scores[len(scores)//2:]) / (len(scores) - len(scores)//2)
                improvement = recent_avg - early_avg
                
                if improvement > 5:
                    trend_insights.append(f"{product} is working well for you - your skin improved by {improvement:.1f} points since starting it")
                elif improvement < -5:
                    trend_insights.append(f"{product} may not be suitable for your skin - consider discontinuing or trying alternatives")
        
        return "\n".join(trend_insights) if trend_insights else "No significant trends detected in your routine"
    
    def _format_smart_insights(self, smart_analysis: Dict) -> List[str]:
        """Format smart analysis insights for LLM context"""
        insights = []
        
        # Feature improvements
        feature_improvements = smart_analysis.get('feature_improvements', [])
        for improvement in feature_improvements:
            if improvement.get('confidence', 0) > 0.5 and improvement.get('improvement', 0) > 3:  # Lowered thresholds
                feature_name = improvement.get('feature', '').replace('_', ' ').title()
                improvement_value = improvement.get('improvement', 0)
                products = improvement.get('products_involved', [])
                
                if products:
                    insights.append(f"• {feature_name} improved by {improvement_value:.1f} points - your {', '.join(products)} routine is working!")
                else:
                    insights.append(f"• {feature_name} improved by {improvement_value:.1f} points - great progress!")
        
        # Product impacts
        product_impacts = smart_analysis.get('product_impacts', [])
        for impact in product_impacts:
            if impact.get('confidence_score', 0) > 0.7 and impact.get('overall_effectiveness', 0) > 10:
                product_name = impact.get('product_name', '')
                effectiveness = impact.get('overall_effectiveness', 0)
                insights.append(f"• {product_name} is highly effective (score: {effectiveness:.1f}) - keep using it!")
            elif impact.get('confidence_score', 0) > 0.6 and impact.get('overall_effectiveness', 0) < -5:
                product_name = impact.get('product_name', '')
                effectiveness = impact.get('overall_effectiveness', 0)
                insights.append(f"• {product_name} may not be suitable (score: {effectiveness:.1f}) - consider alternatives")
        
        # Smart insights
        smart_insights = smart_analysis.get('smart_insights', [])
        for insight in smart_insights:
            if insight.get('confidence', 0) > 0.7 and insight.get('priority') == 'high':
                title = insight.get('title', '')
                description = insight.get('description', '')
                insights.append(f"• {title}: {description}")
        
        # Trust metrics
        trust_metrics = smart_analysis.get('trust_metrics', {})
        trust_score = trust_metrics.get('trust_score', 0)
        if trust_score > 0.8:
            insights.append(f"• High confidence analysis (trust score: {trust_score:.2f}) - these insights are reliable")
        elif trust_score > 0.6:
            insights.append(f"• Moderate confidence analysis (trust score: {trust_score:.2f}) - monitor for more data")
        
        return insights if insights else ["No significant product correlations detected yet - keep tracking your routine"]
    
    def _analyze_feature_correlations(self, analysis_data: Dict, routine_data: Optional[Dict] = None) -> str:
        """Advanced correlation analysis between features and lifestyle factors"""
        features = analysis_data.get('features', {})
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        
        correlations = []
        
        # Sleep-Feature Correlations
        if sleep_score < 50:
            if features.get('dark_circles', 0) < -20:
                correlations.append("Strong correlation: Poor sleep (score {}) directly linked to prominent dark circles (-{})".format(sleep_score, abs(features.get('dark_circles', 0))))
            if features.get('puffiness', 0) < -15:
                correlations.append("Moderate correlation: Insufficient sleep contributing to eye puffiness (-{})".format(abs(features.get('puffiness', 0))))
        
        # Hydration-Feature Correlations
        if routine_data:
            water_intake = routine_data.get('water_intake', 0)
            if water_intake < 6:
                if features.get('brightness', 0) < 0:
                    correlations.append("Strong correlation: Low hydration ({} glasses) linked to dull skin brightness (-{})".format(water_intake, abs(features.get('brightness', 0))))
                if features.get('texture', 0) < -10:
                    correlations.append("Moderate correlation: Dehydration affecting skin texture (-{})".format(abs(features.get('texture', 0))))
        
        # Skincare-Feature Correlations
        if routine_data and routine_data.get('skincare_products'):
            products = routine_data.get('skincare_products', [])
            if 'vitamin_c' in str(products).lower() and features.get('brightness', 0) > 10:
                correlations.append("Positive correlation: Vitamin C usage showing improved skin brightness (+{})".format(features.get('brightness', 0)))
            if 'retinol' in str(products).lower() and features.get('wrinkles', 0) > -20:
                correlations.append("Positive correlation: Retinol usage improving wrinkle appearance")
        
        # Stress-Feature Correlations
        if routine_data and routine_data.get('daily_note'):
            daily_note = routine_data.get('daily_note', '').lower()
            if any(word in daily_note for word in ['stress', 'stressed', 'anxious', 'worried']):
                if features.get('dark_circles', 0) < -25:
                    correlations.append("High correlation: Stress mentioned in notes strongly linked to dark circles (-{})".format(abs(features.get('dark_circles', 0))))
        
        return "\n".join(correlations) if correlations else "No significant correlations detected - continue tracking for pattern recognition"
    
    def _assess_health_risks(self, analysis_data: Dict, routine_data: Optional[Dict] = None) -> str:
        """Advanced health risk assessment based on scores and lifestyle"""
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        features = analysis_data.get('features', {})
        
        risks = []
        risk_level = "LOW"
        
        # Sleep-related risks
        if sleep_score < 30:
            risks.append("HIGH RISK: Critical sleep deficiency - may lead to chronic fatigue, weakened immune system, and accelerated aging")
            risk_level = "HIGH"
        elif sleep_score < 50:
            risks.append("MODERATE RISK: Poor sleep quality - may cause cognitive decline and skin health deterioration")
            risk_level = "MODERATE"
        
        # Skin health risks
        if skin_score < 30:
            risks.append("HIGH RISK: Poor skin health - may indicate underlying health issues, dehydration, or poor nutrition")
            risk_level = "HIGH"
        elif skin_score < 50:
            risks.append("MODERATE RISK: Suboptimal skin health - may lead to premature aging and skin sensitivity")
            risk_level = "MODERATE"
        
        # Feature-specific risks
        if features.get('dark_circles', 0) < -50:
            risks.append("MODERATE RISK: Severe dark circles - may indicate sleep apnea, allergies, or circulatory issues")
        if features.get('wrinkles', 0) < -50:
            risks.append("MODERATE RISK: Advanced wrinkles - may indicate excessive sun exposure or premature aging")
        if features.get('texture', 0) < -50:
            risks.append("LOW RISK: Poor skin texture - may indicate dehydration or lack of proper skincare")
        
        # Lifestyle risk factors
        if routine_data:
            sleep_hours = routine_data.get('sleep_hours', 0)
            water_intake = routine_data.get('water_intake', 0)
            
            if sleep_hours < 5:
                risks.append("HIGH RISK: Chronic sleep deprivation - severe health implications")
                risk_level = "HIGH"
            if water_intake < 4:
                risks.append("MODERATE RISK: Severe dehydration - may cause kidney issues and skin problems")
                risk_level = "MODERATE"
        
        risk_summary = f"Overall Risk Level: {risk_level}"
        if risks:
            return risk_summary + "\n" + "\n".join(risks)
        else:
            return risk_summary + "\nNo significant health risks detected - maintain current healthy habits"
    
    def _generate_personalized_context(self, analysis_data: Dict, routine_data: Optional[Dict] = None) -> str:
        """Generate personalized context based on user's specific patterns and preferences"""
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        features = analysis_data.get('features', {})
        
        personalization = []
        
        # Personalized sleep profile
        if sleep_score >= 70:
            personalization.append("Sleep Champion: Excellent sleep habits - maintain this routine for optimal health")
        elif sleep_score >= 50:
            personalization.append("Sleep Optimizer: Good foundation - focus on consistency and quality improvement")
        else:
            personalization.append("Sleep Transformer: Priority focus area - sleep improvement will have the biggest impact on overall health")
        
        # Personalized skin profile
        if skin_score >= 70:
            personalization.append("Skin Glow Master: Excellent skin health - focus on maintenance and prevention")
        elif skin_score >= 50:
            personalization.append("Skin Enhancer: Good skin condition - target specific concerns for improvement")
        else:
            personalization.append("Skin Rejuvenator: Focus area - comprehensive skincare routine needed")
        
        # Personalized feature focus
        worst_feature = min(features.items(), key=lambda x: x[1]) if features else None
        if worst_feature and worst_feature[1] < -30:
            feature_name = worst_feature[0].replace('_', ' ').title()
            personalization.append(f"Priority Focus: {feature_name} is your main concern (-{abs(worst_feature[1])}) - targeted treatment recommended")
        
        # Personalized routine insights
        if routine_data:
            sleep_hours = routine_data.get('sleep_hours', 0)
            water_intake = routine_data.get('water_intake', 0)
            products = routine_data.get('skincare_products', [])
            
            if sleep_hours > 0:
                if sleep_hours >= 8:
                    personalization.append("Sleep Routine: Excellent sleep duration - this is your strength")
                elif sleep_hours < 6:
                    personalization.append("Sleep Routine: Critical improvement needed - this is your biggest opportunity")
            
            if water_intake > 0:
                if water_intake >= 8:
                    personalization.append("Hydration: Excellent water intake - maintain this habit")
                elif water_intake < 6:
                    personalization.append("Hydration: Increase water intake - this will improve skin plumpness")
            
            if products:
                personalization.append(f"Skincare Routine: {len(products)} products detected - comprehensive routine in place")
            else:
                personalization.append("Skincare Routine: Basic routine needed - start with cleanser, moisturizer, sunscreen")
        
        return "\n".join(personalization) if personalization else "Continue tracking for personalized insights"
    
    def _create_dynamic_context(self, analysis_data: Dict, routine_data: Optional[Dict] = None, historical_data: Optional[List[Dict]] = None) -> str:
        """Create dynamic context that adapts based on user's specific patterns"""
        
        # Analyze user's wellness profile
        profile = self._create_wellness_profile(analysis_data, routine_data, historical_data)
        
        # Generate personalized context sections
        context_sections = {
            'current_state': self._analyze_current_state(analysis_data),
            'lifestyle_analysis': self._deep_lifestyle_analysis(routine_data),
            'historical_patterns': self._analyze_historical_patterns(historical_data),
            'risk_assessment': self._assess_comprehensive_risks(analysis_data, routine_data),
            'opportunity_analysis': self._identify_optimization_opportunities(analysis_data, routine_data),
            'personalization_data': profile
        }
        
        return self._compile_context_sections(context_sections)

    def _create_wellness_profile(self, analysis_data: Dict, routine_data: Optional[Dict], historical_data: Optional[List[Dict]]) -> Dict:
        """Create comprehensive wellness profile"""
        
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        
        profile = {
            'wellness_tier': self._determine_wellness_tier(sleep_score, skin_score),
            'primary_challenges': self._identify_primary_challenges(analysis_data),
            'lifestyle_consistency': self._assess_lifestyle_consistency(routine_data, historical_data),
            'improvement_potential': self._calculate_improvement_potential(analysis_data, routine_data),
            'expertise_level': self._determine_user_expertise_level(routine_data),
            'motivation_style': self._determine_motivation_style(sleep_score, skin_score)
        }
        
        return profile

    def _determine_wellness_tier(self, sleep_score: int, skin_score: int) -> str:
        """Determine user's current wellness tier"""
        avg_score = (sleep_score + skin_score) / 2
        
        if avg_score >= 85:
            return "Elite Performer"
        elif avg_score >= 70:
            return "Advanced Optimizer"
        elif avg_score >= 55:
            return "Solid Foundation"
        elif avg_score >= 40:
            return "Active Improver"
        else:
            return "Transformation Candidate"
    
    def _identify_primary_challenges(self, analysis_data: Dict) -> List[str]:
        """Identify user's primary wellness challenges"""
        challenges = []
        features = analysis_data.get('features', {})
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        
        if sleep_score < 50:
            challenges.append("Sleep Quality")
        if skin_score < 50:
            challenges.append("Skin Health")
        if features.get('dark_circles', 0) < -30:
            challenges.append("Dark Circles")
        if features.get('puffiness', 0) < -20:
            challenges.append("Eye Puffiness")
        if features.get('wrinkles', 0) < -30:
            challenges.append("Aging Signs")
        if features.get('texture', 0) < -20:
            challenges.append("Skin Texture")
        if features.get('brightness', 0) < 0:
            challenges.append("Skin Dullness")
        
        return challenges[:3]  # Top 3 challenges
    
    def _assess_lifestyle_consistency(self, routine_data: Optional[Dict], historical_data: Optional[List[Dict]]) -> str:
        """Assess how consistent user's lifestyle patterns are"""
        if not routine_data and not historical_data:
            return "Unknown - No data available"
        
        consistency_score = 0
        factors = 0
        
        if routine_data:
            if routine_data.get('sleep_hours', 0) > 0:
                consistency_score += 1
                factors += 1
            if routine_data.get('water_intake', 0) > 0:
                consistency_score += 1
                factors += 1
            if routine_data.get('skincare_products'):
                consistency_score += 1
                factors += 1
        
        if factors == 0:
            return "No routine data"
        
        consistency_percentage = (consistency_score / factors) * 100
        
        if consistency_percentage >= 80:
            return "Highly Consistent"
        elif consistency_percentage >= 60:
            return "Moderately Consistent"
        else:
            return "Inconsistent"
    
    def _calculate_improvement_potential(self, analysis_data: Dict, routine_data: Optional[Dict]) -> str:
        """Calculate how much improvement potential the user has"""
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        avg_score = (sleep_score + skin_score) / 2
        
        if avg_score < 30:
            return "High - Major improvements possible"
        elif avg_score < 50:
            return "Very High - Significant improvements possible"
        elif avg_score < 70:
            return "Moderate - Good improvements possible"
        elif avg_score < 85:
            return "Low - Fine-tuning possible"
        else:
            return "Minimal - Maintenance focus"
    
    def _determine_user_expertise_level(self, routine_data: Optional[Dict]) -> str:
        """Determine user's skincare and wellness expertise level"""
        if not routine_data:
            return "Beginner"
        
        products = routine_data.get('skincare_products', [])
        expertise_score = 0
        
        # Advanced products indicate higher expertise
        advanced_products = ['retinol', 'vitamin_c', 'peptide', 'aha', 'bha', 'azelaic']
        for product in products:
            if any(advanced in str(product).lower() for advanced in advanced_products):
                expertise_score += 1
        
        if expertise_score >= 3:
            return "Advanced"
        elif expertise_score >= 1:
            return "Intermediate"
        else:
            return "Beginner"
    
    def _determine_motivation_style(self, sleep_score: int, skin_score: int) -> str:
        """Determine what motivates this user based on their scores"""
        avg_score = (sleep_score + skin_score) / 2
        
        if avg_score < 40:
            return "Transformation - Needs dramatic change motivation"
        elif avg_score < 60:
            return "Improvement - Needs steady progress motivation"
        elif avg_score < 80:
            return "Optimization - Needs fine-tuning motivation"
        else:
            return "Maintenance - Needs consistency motivation"
    
    def _analyze_current_state(self, analysis_data: Dict) -> str:
        """Analyze current wellness state with detailed insights"""
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        features = analysis_data.get('features', {})
        
        state_analysis = f"""
        Current Wellness State Analysis:
        - Sleep Health: {sleep_score}/100 ({'Excellent' if sleep_score >= 80 else 'Good' if sleep_score >= 60 else 'Needs Improvement'})
        - Skin Health: {skin_score}/100 ({'Excellent' if skin_score >= 80 else 'Good' if skin_score >= 60 else 'Needs Improvement'})
        - Overall Status: {self._determine_wellness_tier(sleep_score, skin_score)}
        """
        
        # Add feature-specific analysis
        feature_analysis = []
        for feature, score in features.items():
            if score < -20:
                feature_analysis.append(f"- {feature.replace('_', ' ').title()}: Significant concern ({score})")
            elif score < 0:
                feature_analysis.append(f"- {feature.replace('_', ' ').title()}: Mild concern ({score})")
            elif score > 20:
                feature_analysis.append(f"- {feature.replace('_', ' ').title()}: Excellent ({score})")
        
        if feature_analysis:
            state_analysis += "\nFeature Analysis:\n" + "\n".join(feature_analysis)
        
        return state_analysis
    
    def _deep_lifestyle_analysis(self, routine_data: Optional[Dict]) -> str:
        """Perform deep analysis of lifestyle factors"""
        if not routine_data:
            return "No lifestyle data available - tracking recommended"
        
        analysis = "Lifestyle Analysis:\n"
        
        # Sleep analysis
        sleep_hours = routine_data.get('sleep_hours', 0)
        if sleep_hours > 0:
            if sleep_hours >= 8:
                analysis += f"- Sleep: Excellent duration ({sleep_hours}h) - optimal for skin repair\n"
            elif sleep_hours >= 7:
                analysis += f"- Sleep: Good duration ({sleep_hours}h) - adequate for recovery\n"
            elif sleep_hours >= 6:
                analysis += f"- Sleep: Adequate duration ({sleep_hours}h) - consider 7-8h for optimal health\n"
            else:
                analysis += f"- Sleep: Insufficient duration ({sleep_hours}h) - critical improvement needed\n"
        
        # Hydration analysis
        water_intake = routine_data.get('water_intake', 0)
        if water_intake > 0:
            if water_intake >= 8:
                analysis += f"- Hydration: Excellent intake ({water_intake} glasses) - optimal for skin plumpness\n"
            elif water_intake >= 6:
                analysis += f"- Hydration: Good intake ({water_intake} glasses) - adequate for skin health\n"
            else:
                analysis += f"- Hydration: Low intake ({water_intake} glasses) - increase for better skin appearance\n"
        
        # Skincare analysis
        products = routine_data.get('skincare_products', [])
        if products:
            analysis += f"- Skincare: {len(products)} products detected - comprehensive routine\n"
            # Analyze product sophistication
            advanced_count = sum(1 for product in products if any(advanced in str(product).lower() 
                                for advanced in ['retinol', 'vitamin_c', 'peptide', 'aha', 'bha']))
            if advanced_count >= 2:
                analysis += "  - Advanced routine detected - sophisticated approach\n"
            elif advanced_count >= 1:
                analysis += "  - Intermediate routine detected - good foundation\n"
            else:
                analysis += "  - Basic routine detected - consider adding targeted treatments\n"
        else:
            analysis += "- Skincare: No products specified - basic routine recommended\n"
        
        return analysis
    
    def _analyze_historical_patterns(self, historical_data: Optional[List[Dict]]) -> str:
        """Analyze historical patterns and trends"""
        if not historical_data or len(historical_data) < 3:
            return "Insufficient historical data for pattern analysis"
        
        # Analyze trends over time
        recent_scores = [entry.get('sleep_score', 0) for entry in historical_data[-3:]]
        earlier_scores = [entry.get('sleep_score', 0) for entry in historical_data[:3]]
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        earlier_avg = sum(earlier_scores) / len(earlier_scores)
        sleep_trend = recent_avg - earlier_avg
        
        recent_skin = [entry.get('skin_health_score', 0) for entry in historical_data[-3:]]
        earlier_skin = [entry.get('skin_health_score', 0) for entry in historical_data[:3]]
        
        recent_skin_avg = sum(recent_skin) / len(recent_skin)
        earlier_skin_avg = sum(earlier_skin) / len(earlier_skin)
        skin_trend = recent_skin_avg - earlier_skin_avg
        
        pattern_analysis = f"Historical Pattern Analysis:\n"
        
        if sleep_trend > 5:
            pattern_analysis += f"- Sleep Trend: Improving (+{sleep_trend:.1f} points) - great progress!\n"
        elif sleep_trend < -5:
            pattern_analysis += f"- Sleep Trend: Declining ({sleep_trend:.1f} points) - attention needed\n"
        else:
            pattern_analysis += f"- Sleep Trend: Stable ({sleep_trend:.1f} points) - consistent performance\n"
        
        if skin_trend > 5:
            pattern_analysis += f"- Skin Trend: Improving (+{skin_trend:.1f} points) - excellent progress!\n"
        elif skin_trend < -5:
            pattern_analysis += f"- Skin Trend: Declining ({skin_trend:.1f} points) - intervention needed\n"
        else:
            pattern_analysis += f"- Skin Trend: Stable ({skin_trend:.1f} points) - maintaining status\n"
        
        return pattern_analysis
    
    def _assess_comprehensive_risks(self, analysis_data: Dict, routine_data: Optional[Dict]) -> str:
        """Comprehensive risk assessment"""
        risks = []
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        
        # Health risks
        if sleep_score < 30:
            risks.append("CRITICAL: Severe sleep deprivation - immediate intervention required")
        elif sleep_score < 50:
            risks.append("HIGH: Poor sleep quality - cognitive and physical health risks")
        
        if skin_score < 30:
            risks.append("HIGH: Poor skin health - may indicate underlying health issues")
        
        # Lifestyle risks
        if routine_data:
            sleep_hours = routine_data.get('sleep_hours', 0)
            if sleep_hours < 5:
                risks.append("CRITICAL: Chronic sleep deprivation - severe health implications")
            
            water_intake = routine_data.get('water_intake', 0)
            if water_intake < 4:
                risks.append("MODERATE: Severe dehydration - kidney and skin health risks")
        
        if not risks:
            return "LOW RISK: No significant health risks detected - maintain current habits"
        
        return "Risk Assessment:\n" + "\n".join(f"- {risk}" for risk in risks)
    
    def _identify_optimization_opportunities(self, analysis_data: Dict, routine_data: Optional[Dict]) -> str:
        """Identify specific optimization opportunities"""
        opportunities = []
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        
        if sleep_score < 70:
            opportunities.append("Sleep Optimization: Focus on sleep quality and duration")
        if skin_score < 70:
            opportunities.append("Skin Enhancement: Implement targeted skincare routine")
        
        if routine_data:
            sleep_hours = routine_data.get('sleep_hours', 0)
            if sleep_hours < 8:
                opportunities.append("Sleep Duration: Aim for 7-9 hours nightly")
            
            water_intake = routine_data.get('water_intake', 0)
            if water_intake < 8:
                opportunities.append("Hydration Boost: Increase to 8+ glasses daily")
            
            products = routine_data.get('skincare_products', [])
            if not products:
                opportunities.append("Skincare Foundation: Establish basic routine")
            elif len(products) < 3:
                opportunities.append("Skincare Enhancement: Add targeted treatments")
        
        if not opportunities:
            return "OPTIMIZATION: Focus on maintenance and fine-tuning current routine"
        
        return "Optimization Opportunities:\n" + "\n".join(f"- {opp}" for opp in opportunities)
    
    def _compile_context_sections(self, context_sections: Dict) -> str:
        """Compile all context sections into final context"""
        compiled_context = ""
        
        for section_name, section_content in context_sections.items():
            if section_content:
                compiled_context += f"\n{section_name.upper().replace('_', ' ')}:\n{section_content}\n"
        
        return compiled_context
    
    def _calculate_analysis_confidence(self, analysis_data: Dict, routine_data: Optional[Dict]) -> float:
        """Calculate confidence score for the analysis"""
        confidence_factors = 0
        total_factors = 0
        
        # Data completeness factor
        if analysis_data.get('sleep_score') is not None:
            confidence_factors += 1
        total_factors += 1
        
        if analysis_data.get('skin_health_score') is not None:
            confidence_factors += 1
        total_factors += 1
        
        if analysis_data.get('features'):
            confidence_factors += 1
        total_factors += 1
        
        # Routine data factor
        if routine_data:
            if routine_data.get('sleep_hours'):
                confidence_factors += 0.5
            if routine_data.get('water_intake'):
                confidence_factors += 0.5
            if routine_data.get('skincare_products'):
                confidence_factors += 0.5
            total_factors += 1.5
        
        # Calculate final confidence
        if total_factors == 0:
            return 0.5  # Default moderate confidence
        
        base_confidence = confidence_factors / total_factors
        
        # Adjust based on data quality
        if base_confidence >= 0.8:
            return min(0.95, base_confidence + 0.1)
        elif base_confidence >= 0.6:
            return base_confidence
        else:
            return max(0.3, base_confidence - 0.1)

class AdvancedInsightsEngine:
    """Generate world-class insights using advanced analytics"""
    
    def __init__(self):
        self.insight_generators = {
            'correlation_insights': self._generate_correlation_insights,
            'trend_insights': self._generate_trend_insights,
            'prediction_insights': self._generate_prediction_insights,
            'optimization_insights': self._generate_optimization_insights,
            'risk_insights': self._generate_risk_insights
        }
    
    def generate_advanced_insights(self, analysis_data: Dict, routine_data: Dict, historical_data: List) -> List[Dict]:
        """Generate sophisticated insights across multiple dimensions"""
        
        all_insights = []
        
        for generator_name, generator_func in self.insight_generators.items():
            insights = generator_func(analysis_data, routine_data, historical_data)
            all_insights.extend(insights)
        
        # Rank insights by importance and confidence
        ranked_insights = self._rank_insights(all_insights)
        
        return ranked_insights[:7]  # Return top 7 insights
    
    def _generate_correlation_insights(self, analysis_data: Dict, routine_data: Dict, historical_data: List) -> List[Dict]:
        """Generate insights about correlations between factors"""
        insights = []
        
        features = analysis_data.get('features', {})
        sleep_hours = routine_data.get('sleep_hours', 0)
        water_intake = routine_data.get('water_intake', 0)
        
        # Sleep-skin correlations
        if sleep_hours < 6 and features.get('dark_circles', 0) < -30:
            insights.append({
                'text': f"Strong correlation detected: Your {sleep_hours}-hour sleep schedule is directly contributing to prominent dark circles (score: {features.get('dark_circles', 0)}). Increasing sleep to 7+ hours could improve this by 40-60% within 2 weeks.",
                'confidence': 9,
                'category': 'correlation',
                'impact': 'high',
                'timeframe': '2-4 weeks'
            })
        
        # Hydration-brightness correlations
        if water_intake < 6 and features.get('brightness', 0) < -20:
            insights.append({
                'text': f"Dehydration correlation: Your {water_intake}-glass water intake is limiting skin radiance (brightness: {features.get('brightness', 0)}). Increasing to 8+ glasses could boost brightness by 30-50% within 1 week.",
                'confidence': 8,
                'category': 'correlation',
                'impact': 'medium',
                'timeframe': '1-2 weeks'
            })
        
        return insights
    
    def _generate_trend_insights(self, analysis_data: Dict, routine_data: Dict, historical_data: List) -> List[Dict]:
        """Generate insights about trends over time"""
        insights = []
        
        if len(historical_data) < 3:
            return insights
        
        # Analyze sleep trends
        recent_sleep = [entry.get('sleep_score', 0) for entry in historical_data[-3:]]
        earlier_sleep = [entry.get('sleep_score', 0) for entry in historical_data[:3]]
        
        recent_avg = sum(recent_sleep) / len(recent_sleep)
        earlier_avg = sum(earlier_sleep) / len(earlier_sleep)
        sleep_trend = recent_avg - earlier_avg
        
        if sleep_trend > 10:
            insights.append({
                'text': f"Excellent progress! Your sleep quality has improved by {sleep_trend:.1f} points over recent weeks. This upward trend suggests your current routine is working effectively.",
                'confidence': 8,
                'category': 'trend',
                'impact': 'high',
                'timeframe': 'ongoing'
            })
        elif sleep_trend < -10:
            insights.append({
                'text': f"Attention needed: Your sleep quality has declined by {abs(sleep_trend):.1f} points recently. This downward trend may be affecting your skin health and overall wellness.",
                'confidence': 9,
                'category': 'trend',
                'impact': 'high',
                'timeframe': 'immediate'
            })
        
        return insights
    
    def _generate_prediction_insights(self, analysis_data: Dict, routine_data: Dict, historical_data: List) -> List[Dict]:
        """Generate predictive insights about future outcomes"""
        insights = []
        
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        features = analysis_data.get('features', {})
        
        # Predict skin improvement potential
        if skin_score < 60 and features.get('dark_circles', 0) < -20:
            improvement_potential = min(40, (60 - skin_score) * 0.8)
            insights.append({
                'text': f"High improvement potential: With consistent sleep (7-8h) and proper hydration, your skin health could improve by {improvement_potential:.0f} points within 4-6 weeks, significantly reducing dark circles.",
                'confidence': 7,
                'category': 'prediction',
                'impact': 'high',
                'timeframe': '4-6 weeks'
            })
        
        # Predict risk factors
        if sleep_score < 40:
            insights.append({
                'text': f"Risk prediction: At your current sleep score of {sleep_score}, you're at high risk for accelerated aging, cognitive decline, and immune system weakening within 2-3 months if patterns don't improve.",
                'confidence': 8,
                'category': 'prediction',
                'impact': 'high',
                'timeframe': '2-3 months'
            })
        
        return insights
    
    def _generate_optimization_insights(self, analysis_data: Dict, routine_data: Dict, historical_data: List) -> List[Dict]:
        """Generate insights about optimization opportunities"""
        insights = []
        
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        features = analysis_data.get('features', {})
        
        # Sleep optimization
        if sleep_score < 70:
            potential_improvement = min(30, 100 - sleep_score)
            insights.append({
                'text': f"Sleep optimization opportunity: Your current {sleep_score}/100 sleep score has {potential_improvement} points of improvement potential. Focus on sleep hygiene, consistent bedtime, and 7-9 hour duration.",
                'confidence': 8,
                'category': 'optimization',
                'impact': 'high',
                'timeframe': '2-4 weeks'
            })
        
        # Skincare optimization
        if skin_score < 70 and features.get('texture', 0) < -10:
            insights.append({
                'text': f"Skincare enhancement needed: Your skin texture score of {features.get('texture', 0)} indicates room for improvement. Consider adding gentle exfoliation (AHA/BHA) and hydrating serums to your routine.",
                'confidence': 7,
                'category': 'optimization',
                'impact': 'medium',
                'timeframe': '3-6 weeks'
            })
        
        return insights
    
    def _generate_risk_insights(self, analysis_data: Dict, routine_data: Dict, historical_data: List) -> List[Dict]:
        """Generate insights about health and wellness risks"""
        insights = []
        
        sleep_score = analysis_data.get('sleep_score', 0)
        skin_score = analysis_data.get('skin_health_score', 0)
        features = analysis_data.get('features', {})
        
        # Critical sleep risks
        if sleep_score < 30:
            insights.append({
                'text': f"CRITICAL RISK: Your sleep score of {sleep_score} indicates severe sleep deprivation. This poses immediate risks to cognitive function, immune system, and long-term health. Professional intervention recommended.",
                'confidence': 10,
                'category': 'risk',
                'impact': 'critical',
                'timeframe': 'immediate'
            })
        
        # Skin health risks
        if skin_score < 30 and features.get('wrinkles', 0) < -40:
            insights.append({
                'text': f"High skin aging risk: Your combination of low skin health ({skin_score}) and significant wrinkles ({features.get('wrinkles', 0)}) suggests accelerated aging. Immediate lifestyle changes and dermatologist consultation recommended.",
                'confidence': 8,
                'category': 'risk',
                'impact': 'high',
                'timeframe': '1-2 weeks'
            })
        
        return insights
    
    def _rank_insights(self, insights: List[Dict]) -> List[Dict]:
        """Rank insights by importance, confidence, and impact"""
        
        def insight_score(insight):
            confidence = insight.get('confidence', 5)
            impact_scores = {'critical': 5, 'high': 3, 'medium': 2, 'low': 1}
            impact = impact_scores.get(insight.get('impact', 'low'), 1)
            
            return confidence * impact
        
        return sorted(insights, key=insight_score, reverse=True)

# Global instance
llm_service = FlexibleLLMService()

