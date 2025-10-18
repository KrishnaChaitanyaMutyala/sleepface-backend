import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ScrollView,
  Modal,
  FlatList,
  Animated,
  TextInput,
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { SKINCARE_PRODUCTS, getProductsByCategory } from '../data/skincareProducts';
import { SkincareProduct } from '../types';
import CustomIcon from './CustomIcon';
import { Colors, Typography, Spacing, BorderRadius, Shadows } from '../design/DesignSystem';

interface SkincareMultiSelectProps {
  selectedProducts: string[];
  onSelectionChange: (products: string[]) => void;
  placeholder?: string;
}

// ============================================================================
// ANIMATED PRODUCT CARD
// ============================================================================
const ProductCard: React.FC<{
  product: SkincareProduct;
  isSelected: boolean;
  onToggle: () => void;
  categoryColor: string;
}> = ({ product, isSelected, onToggle, categoryColor }) => {
  const scaleAnim = React.useRef(new Animated.Value(1)).current;

  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.98,
      useNativeDriver: true,
      tension: 100,
      friction: 3,
    }).start();
  };

  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
      tension: 100,
      friction: 3,
    }).start();
  };

  return (
    <TouchableOpacity
      onPress={onToggle}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      activeOpacity={1}
    >
      <Animated.View
        style={[
          styles.productCard,
          isSelected && styles.productCardSelected,
          { transform: [{ scale: scaleAnim }] },
        ]}
      >
        {/* Selection Indicator */}
        <View style={[styles.selectionIndicator, { backgroundColor: categoryColor }]} />
        
        <View style={styles.productCardContent}>
          {/* Product Header */}
          <View style={styles.productHeader}>
            <View style={styles.productTitleRow}>
              <Text style={[styles.productName, isSelected && styles.productNameSelected]}>
                {product.name}
              </Text>
              <View
                style={[
                  styles.checkCircle,
                  isSelected && styles.checkCircleSelected,
                  { borderColor: isSelected ? categoryColor : '#374151' },
                ]}
              >
                {isSelected && (
                  <CustomIcon name="check" size={14} color={categoryColor} />
                )}
              </View>
            </View>
          </View>

          {/* Product Meta */}
          <View style={styles.productMeta}>
            <View style={[styles.categoryBadge, { backgroundColor: categoryColor + '20' }]}>
              <Text style={[styles.categoryBadgeText, { color: categoryColor }]}>
                {product.category}
              </Text>
            </View>
            <Text style={styles.usageBadge}>• {product.usage}</Text>
          </View>

          {/* Benefits */}
          <View style={styles.benefitsContainer}>
            {product.benefits.slice(0, 2).map((benefit, index) => (
              <View key={index} style={styles.benefitRow}>
                <View style={[styles.benefitDot, { backgroundColor: categoryColor + '60' }]} />
                <Text style={styles.benefitText} numberOfLines={1}>
                  {benefit}
                </Text>
              </View>
            ))}
            {product.benefits.length > 2 && (
              <Text style={styles.moreBenefits}>
                +{product.benefits.length - 2} more benefits
              </Text>
            )}
          </View>
        </View>
      </Animated.View>
    </TouchableOpacity>
  );
};

// ============================================================================
// MAIN COMPONENT
// ============================================================================
const SkincareMultiSelect: React.FC<SkincareMultiSelectProps> = ({
  selectedProducts,
  onSelectionChange,
  placeholder = "Select skincare products..."
}) => {
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const categories = [
    { id: 'all', name: 'All Products', icon: 'grid' },
    { id: 'cleanser', name: 'Cleansers', icon: 'droplet' },
    { id: 'moisturizer', name: 'Moisturizers', icon: 'sparkles' },
    { id: 'serum', name: 'Serums', icon: 'zap' },
    { id: 'sunscreen', name: 'Sunscreen', icon: 'sun' },
    { id: 'treatment', name: 'Treatments', icon: 'heart' },
    { id: 'mask', name: 'Masks', icon: 'star' },
    { id: 'toner', name: 'Toners', icon: 'droplet' },
    { id: 'exfoliant', name: 'Exfoliants', icon: 'layers' },
  ];

  const getCategoryColor = (category: string) => {
    const colors: { [key: string]: string } = {
      cleanser: '#3B82F6',
      moisturizer: '#10B981',
      serum: '#8B5CF6',
      sunscreen: '#F59E0B',
      treatment: '#EF4444',
      mask: '#EC4899',
      toner: '#06B6D4',
      exfoliant: '#84CC16',
      all: '#6366F1',
    };
    return colors[category] || '#6B7280';
  };

  const toggleProduct = (productId: string) => {
    if (selectedProducts.includes(productId)) {
      onSelectionChange(selectedProducts.filter(id => id !== productId));
    } else {
      onSelectionChange([...selectedProducts, productId]);
    }
  };

  const getSelectedProductNames = () => {
    return selectedProducts.map(id => {
      const product = SKINCARE_PRODUCTS.find(p => p.id === id);
      return product ? product.name : id;
    });
  };

  const getFilteredProducts = () => {
    let products = SKINCARE_PRODUCTS;
    
    // Filter by category
    if (selectedCategory && selectedCategory !== 'all') {
      products = products.filter(p => p.category === selectedCategory);
    }
    
    // Filter by search
    if (searchQuery.trim()) {
      products = products.filter(p =>
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.category.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.benefits.some(b => b.toLowerCase().includes(searchQuery.toLowerCase()))
      );
    }
    
    return products;
  };

  const clearAll = () => {
    onSelectionChange([]);
  };

  const filteredProducts = getFilteredProducts();

  return (
    <View style={styles.container}>
      {/* Selector Button */}
      <TouchableOpacity
        style={styles.selector}
        onPress={() => setIsModalVisible(true)}
        activeOpacity={0.8}
      >
        <LinearGradient
          colors={selectedProducts.length > 0 ? ['#10B98120', '#059D6920'] : ['#374151', '#1F2937']}
          style={styles.selectorGradient}
        >
          <View style={styles.selectorContent}>
            {selectedProducts.length > 0 ? (
              <View style={styles.selectedContainer}>
                <View style={styles.selectedHeader}>
                  <View style={styles.selectedBadge}>
                    <CustomIcon name="check" size={12} color="#10B981" />
                    <Text style={styles.selectedCount}>
                      {selectedProducts.length}
                    </Text>
                  </View>
                  <Text style={styles.selectedLabel}>products selected</Text>
                </View>
                <Text style={styles.selectedNames} numberOfLines={2}>
                  {getSelectedProductNames().join(', ')}
                </Text>
              </View>
            ) : (
              <View style={styles.placeholderContainer}>
                <CustomIcon name="sparkles" size={20} color="#6B7280" />
                <Text style={styles.placeholder}>{placeholder}</Text>
              </View>
            )}
            <CustomIcon name="chevronDown" size={20} color="#9CA3AF" />
          </View>
        </LinearGradient>
      </TouchableOpacity>

      {/* Modal */}
      <Modal
        visible={isModalVisible}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setIsModalVisible(false)}
      >
        <View style={styles.modalContainer}>
          {/* Header */}
          <LinearGradient
            colors={[Colors.primary, Colors.accent]}
            style={styles.modalHeader}
          >
            <View style={styles.modalHeaderContent}>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setIsModalVisible(false)}
              >
                <CustomIcon name="chevronLeft" size={24} color="#FFFFFF" />
              </TouchableOpacity>
              
              <View style={styles.headerCenter}>
                <Text style={styles.modalTitle}>Select Products</Text>
                {selectedProducts.length > 0 && (
                  <Text style={styles.modalSubtitle}>
                    {selectedProducts.length} selected
                  </Text>
                )}
              </View>
              
              {selectedProducts.length > 0 ? (
                <TouchableOpacity style={styles.clearButton} onPress={clearAll}>
                  <Text style={styles.clearButtonText}>Clear</Text>
                </TouchableOpacity>
              ) : (
                <View style={styles.headerSpacer} />
              )}
            </View>

            {/* Search Bar */}
            <View style={styles.searchContainer}>
              <CustomIcon name="search" size={18} color="#9CA3AF" />
              <TextInput
                style={styles.searchInput}
                placeholder="Search products..."
                placeholderTextColor="#6B7280"
                value={searchQuery}
                onChangeText={setSearchQuery}
              />
              {searchQuery.length > 0 && (
                <TouchableOpacity onPress={() => setSearchQuery('')}>
                  <CustomIcon name="close" size={18} color="#9CA3AF" />
                </TouchableOpacity>
              )}
            </View>
          </LinearGradient>

          {/* Category Filter */}
          <View style={styles.categoryFilter}>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={styles.categoryScrollContent}
            >
              {categories.map((category) => {
                const isActive = selectedCategory === category.id || (!selectedCategory && category.id === 'all');
                const categoryColor = getCategoryColor(category.id);
                
                return (
                  <TouchableOpacity
                    key={category.id}
                    style={[
                      styles.categoryChip,
                      isActive && styles.categoryChipActive,
                      isActive && { backgroundColor: categoryColor + '20', borderColor: categoryColor },
                    ]}
                    onPress={() => setSelectedCategory(category.id === 'all' ? null : category.id)}
                  >
                    <CustomIcon
                      name={category.icon as keyof typeof import('../design/DesignSystem').Icons}
                      size={16}
                      color={isActive ? categoryColor : '#9CA3AF'}
                    />
                    <Text
                      style={[
                        styles.categoryChipText,
                        isActive && styles.categoryChipTextActive,
                        isActive && { color: categoryColor },
                      ]}
                    >
                      {category.name}
                    </Text>
                  </TouchableOpacity>
                );
              })}
            </ScrollView>
          </View>

          {/* Products List */}
          <ScrollView
            style={styles.productsScroll}
            contentContainerStyle={styles.productsContent}
            showsVerticalScrollIndicator={false}
          >
            {filteredProducts.length > 0 ? (
              <>
                <Text style={styles.resultCount}>
                  {filteredProducts.length} product{filteredProducts.length !== 1 ? 's' : ''} found
                </Text>
                {filteredProducts.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    isSelected={selectedProducts.includes(product.id)}
                    onToggle={() => toggleProduct(product.id)}
                    categoryColor={getCategoryColor(product.category)}
                  />
                ))}
              </>
            ) : (
              <View style={styles.emptyState}>
                <CustomIcon name="search" size={64} color="#374151" />
                <Text style={styles.emptyStateTitle}>No products found</Text>
                <Text style={styles.emptyStateText}>
                  Try adjusting your search or filters
                </Text>
              </View>
            )}
          </ScrollView>

          {/* Footer */}
          <View style={styles.modalFooter}>
            <TouchableOpacity
              style={styles.doneButton}
              onPress={() => setIsModalVisible(false)}
            >
              <LinearGradient
                colors={[Colors.primary, Colors.accent]}
                style={styles.doneButtonGradient}
              >
                <CustomIcon name="check" size={20} color="#FFFFFF" />
                <Text style={styles.doneButtonText}>
                  Done ({selectedProducts.length})
                </Text>
              </LinearGradient>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
};

// ============================================================================
// STYLES
// ============================================================================
const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  
  // Selector
  selector: {
    borderRadius: 16,
    overflow: 'hidden',
  },
  selectorGradient: {
    padding: 16,
  },
  selectorContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  selectedContainer: {
    flex: 1,
    gap: 8,
  },
  selectedHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  selectedBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: '#10B98120',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  selectedCount: {
    color: '#10B981',
    fontSize: 12,
    fontWeight: '700',
  },
  selectedLabel: {
    color: '#10B981',
    fontSize: 12,
    fontWeight: '600',
  },
  selectedNames: {
    color: '#D1D5DB',
    fontSize: 13,
    lineHeight: 18,
  },
  placeholderContainer: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  placeholder: {
    color: '#6B7280',
    fontSize: 15,
  },
  
  // Modal
  modalContainer: {
    flex: 1,
    backgroundColor: '#111827',
  },
  modalHeader: {
    paddingTop: 60,
    paddingBottom: 20,
    paddingHorizontal: 20,
  },
  modalHeaderContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  closeButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: 'rgba(255,255,255,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerCenter: {
    flex: 1,
    alignItems: 'center',
  },
  modalTitle: {
    color: '#FFFFFF',
    fontSize: 20,
    fontWeight: '800',
  },
  modalSubtitle: {
    color: 'rgba(255,255,255,0.8)',
    fontSize: 13,
    marginTop: 2,
  },
  clearButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.2)',
  },
  clearButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  headerSpacer: {
    width: 40,
  },
  
  // Search
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255,255,255,0.15)',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    gap: 10,
  },
  searchInput: {
    flex: 1,
    color: '#FFFFFF',
    fontSize: 15,
  },
  
  // Category Filter
  categoryFilter: {
    backgroundColor: '#1F2937',
    paddingVertical: 16,
  },
  categoryScrollContent: {
    paddingHorizontal: 20,
    gap: 10,
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    backgroundColor: '#374151',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  categoryChipActive: {
    borderWidth: 2,
  },
  categoryChipText: {
    color: '#9CA3AF',
    fontSize: 14,
    fontWeight: '600',
  },
  categoryChipTextActive: {
    fontWeight: '700',
  },
  
  // Products
  productsScroll: {
    flex: 1,
  },
  productsContent: {
    padding: 20,
  },
  resultCount: {
    color: '#9CA3AF',
    fontSize: 13,
    fontWeight: '600',
    marginBottom: 16,
  },
  
  // Product Card
  productCard: {
    backgroundColor: '#1F2937',
    borderRadius: 16,
    marginBottom: 12,
    overflow: 'hidden',
    borderWidth: 2,
    borderColor: 'transparent',
  },
  productCardSelected: {
    borderColor: '#10B981',
    backgroundColor: '#10B98110',
  },
  selectionIndicator: {
    height: 4,
  },
  productCardContent: {
    padding: 16,
  },
  productHeader: {
    marginBottom: 12,
  },
  productTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  productName: {
    flex: 1,
    color: '#F3F4F6',
    fontSize: 16,
    fontWeight: '700',
    marginRight: 12,
  },
  productNameSelected: {
    color: '#10B981',
  },
  checkCircle: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkCircleSelected: {
    backgroundColor: '#FFFFFF',
  },
  
  // Product Meta
  productMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 12,
  },
  categoryBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 8,
  },
  categoryBadgeText: {
    fontSize: 11,
    fontWeight: '700',
    textTransform: 'uppercase',
  },
  usageBadge: {
    color: '#9CA3AF',
    fontSize: 12,
    fontWeight: '500',
  },
  
  // Benefits
  benefitsContainer: {
    gap: 6,
  },
  benefitRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  benefitDot: {
    width: 4,
    height: 4,
    borderRadius: 2,
  },
  benefitText: {
    flex: 1,
    color: '#D1D5DB',
    fontSize: 13,
    lineHeight: 18,
  },
  moreBenefits: {
    color: '#6B7280',
    fontSize: 12,
    fontStyle: 'italic',
    marginLeft: 12,
  },
  
  // Empty State
  emptyState: {
    alignItems: 'center',
    paddingVertical: 60,
  },
  emptyStateTitle: {
    color: '#F3F4F6',
    fontSize: 18,
    fontWeight: '700',
    marginTop: 16,
    marginBottom: 8,
  },
  emptyStateText: {
    color: '#9CA3AF',
    fontSize: 14,
  },
  
  // Footer
  modalFooter: {
    padding: 20,
    backgroundColor: '#1F2937',
    borderTopWidth: 1,
    borderTopColor: '#374151',
  },
  doneButton: {
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: Colors.primary,
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.3,
    shadowRadius: 12,
    elevation: 8,
  },
  doneButtonGradient: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    gap: 8,
  },
  doneButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
});

export default SkincareMultiSelect;
