#!/usr/bin/env python3
"""
Test script to verify the fixed algorithms are working correctly
"""
import sys
import os
sys.path.append('/Users/chaitanya/sleepface-fresh/backend')

import numpy as np
import cv2
from ai_engine import AIEngine

def test_algorithms():
    """Test the fixed algorithms directly"""
    print("🧪 Testing Fixed Algorithms...")
    
    # Create a test image (100x100 pixels)
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    # Create mock landmarks (simplified face landmarks)
    landmarks = np.array([
        [0.3, 0.3], [0.4, 0.3], [0.5, 0.3], [0.6, 0.3], [0.7, 0.3],  # forehead
        [0.2, 0.4], [0.3, 0.4], [0.4, 0.4], [0.5, 0.4], [0.6, 0.4], [0.7, 0.4], [0.8, 0.4],  # eyes
        [0.3, 0.5], [0.4, 0.5], [0.5, 0.5], [0.6, 0.5], [0.7, 0.5],  # nose
        [0.2, 0.6], [0.3, 0.6], [0.4, 0.6], [0.5, 0.6], [0.6, 0.6], [0.7, 0.6], [0.8, 0.6],  # mouth
        [0.1, 0.7], [0.2, 0.7], [0.3, 0.7], [0.4, 0.7], [0.5, 0.7], [0.6, 0.7], [0.7, 0.7], [0.8, 0.7], [0.9, 0.7],  # chin
    ])
    
    # Initialize AI engine
    ai_engine = AIEngine()
    
    print("🔍 Testing Dark Circles Algorithm...")
    try:
        # Test dark circles with different brightness levels
        bright_image = np.ones((100, 100, 3), dtype=np.uint8) * 200  # Bright
        dark_image = np.ones((100, 100, 3), dtype=np.uint8) * 50     # Dark
        
        bright_score = ai_engine._analyze_dark_circles(bright_image)
        dark_score = ai_engine._analyze_dark_circles(dark_image)
        
        print(f"   Bright image score: {bright_score} (should be positive)")
        print(f"   Dark image score: {dark_score} (should be negative)")
        
        if bright_score > 0 and dark_score < 0:
            print("   ✅ Dark circles algorithm working correctly!")
        else:
            print("   ❌ Dark circles algorithm not working correctly!")
            
    except Exception as e:
        print(f"   ❌ Error testing dark circles: {e}")
    
    print("\n🔍 Testing Texture Algorithm...")
    try:
        # Test texture with different smoothness levels
        smooth_image = np.ones((100, 100, 3), dtype=np.uint8) * 128  # Smooth
        rough_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)  # Rough
        
        smooth_score = ai_engine._analyze_texture(smooth_image, landmarks)
        rough_score = ai_engine._analyze_texture(rough_image, landmarks)
        
        print(f"   Smooth image score: {smooth_score} (should be positive)")
        print(f"   Rough image score: {rough_score} (should be negative)")
        
        if smooth_score > rough_score:
            print("   ✅ Texture algorithm working correctly!")
        else:
            print("   ❌ Texture algorithm not working correctly!")
            
    except Exception as e:
        print(f"   ❌ Error testing texture: {e}")
    
    print("\n🔍 Testing Puffiness Algorithm...")
    try:
        # Test puffiness with different edge densities
        high_edge_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)  # High edges
        low_edge_image = np.ones((100, 100, 3), dtype=np.uint8) * 128  # Low edges
        
        high_edge_score = ai_engine._analyze_puffiness(high_edge_image, landmarks)
        low_edge_score = ai_engine._analyze_puffiness(low_edge_image, landmarks)
        
        print(f"   High edge image score: {high_edge_score} (should be positive)")
        print(f"   Low edge image score: {low_edge_score} (should be negative)")
        
        if high_edge_score > low_edge_score:
            print("   ✅ Puffiness algorithm working correctly!")
        else:
            print("   ❌ Puffiness algorithm not working correctly!")
            
    except Exception as e:
        print(f"   ❌ Error testing puffiness: {e}")
    
    print("\n🔍 Testing Wrinkles Algorithm...")
    try:
        # Test wrinkles with different edge densities
        high_wrinkle_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)  # High edges
        low_wrinkle_image = np.ones((100, 100, 3), dtype=np.uint8) * 128  # Low edges
        
        high_wrinkle_score = ai_engine._analyze_wrinkles(high_wrinkle_image, landmarks)
        low_wrinkle_score = ai_engine._analyze_wrinkles(low_wrinkle_image, landmarks)
        
        print(f"   High wrinkle image score: {high_wrinkle_score} (should be negative)")
        print(f"   Low wrinkle image score: {low_wrinkle_score} (should be positive)")
        
        if high_wrinkle_score < low_wrinkle_score:
            print("   ✅ Wrinkles algorithm working correctly!")
        else:
            print("   ❌ Wrinkles algorithm not working correctly!")
            
    except Exception as e:
        print(f"   ❌ Error testing wrinkles: {e}")
    
    print("\n🔍 Testing Brightness Algorithm...")
    try:
        # Test brightness with different brightness levels
        bright_skin_image = np.ones((100, 100, 3), dtype=np.uint8) * 200  # Bright
        dull_skin_image = np.ones((100, 100, 3), dtype=np.uint8) * 50     # Dull
        
        bright_skin_score = ai_engine._analyze_brightness(bright_skin_image, landmarks)
        dull_skin_score = ai_engine._analyze_brightness(dull_skin_image, landmarks)
        
        print(f"   Bright skin score: {bright_skin_score} (should be positive)")
        print(f"   Dull skin score: {dull_skin_score} (should be negative)")
        
        if bright_skin_score > dull_skin_score:
            print("   ✅ Brightness algorithm working correctly!")
        else:
            print("   ❌ Brightness algorithm not working correctly!")
            
    except Exception as e:
        print(f"   ❌ Error testing brightness: {e}")
    
    print("\n🔍 Testing Pore Size Algorithm...")
    try:
        # Test pore size with different pore patterns
        small_pore_image = np.ones((100, 100, 3), dtype=np.uint8) * 128  # No pores
        large_pore_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)  # Random pattern
        
        small_pore_score = ai_engine._analyze_pore_size(small_pore_image, landmarks)
        large_pore_score = ai_engine._analyze_pore_size(large_pore_image, landmarks)
        
        print(f"   Small pore image score: {small_pore_score} (should be positive)")
        print(f"   Large pore image score: {large_pore_score} (should be negative or lower)")
        
        if small_pore_score >= large_pore_score:
            print("   ✅ Pore size algorithm working correctly!")
        else:
            print("   ❌ Pore size algorithm not working correctly!")
            
    except Exception as e:
        print(f"   ❌ Error testing pore size: {e}")

if __name__ == "__main__":
    test_algorithms()












