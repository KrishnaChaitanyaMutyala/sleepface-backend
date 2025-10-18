import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import { StyleSheet, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Colors, getThemeColors } from './src/design/DesignSystem';

// Import screens
import HomeScreen from './src/screens/HomeScreen';
import CameraScreen from './src/screens/SimpleCameraScreen';
import HistoryScreen from './src/screens/HistoryScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import AnalysisScreen from './src/screens/AnalysisScreen';
import PhotoGalleryScreen from './src/screens/PhotoGalleryScreen';
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';

// Import context providers
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import { AnalysisProvider } from './src/contexts/AnalysisContext';
import { ThemeProvider, useTheme } from './src/contexts/ThemeContext';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function MainTabs() {
  const { isDark } = useTheme();
  const { isGuest } = useAuth();
  const colors = getThemeColors(isDark);
  
  return (
    <Tab.Navigator
      initialRouteName={isGuest ? "Camera" : "Insights"}
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Insights') {
            iconName = focused ? 'analytics' : 'analytics-outline';
          } else if (route.name === 'Camera') {
            iconName = focused ? 'camera' : 'camera-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          } else {
            iconName = 'help-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: Colors.primary,
        tabBarInactiveTintColor: isDark ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.5)',
        tabBarStyle: {
          backgroundColor: isDark ? 'rgba(0, 0, 0, 0.7)' : 'rgba(255, 255, 255, 0.7)',
          borderTopColor: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
          paddingBottom: 12,
          paddingTop: 12,
          height: 80,
          borderTopWidth: 1,
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          backdropFilter: 'blur(60px)',
          shadowColor: isDark ? '#000' : '#000',
          shadowOffset: { width: 0, height: -4 },
          shadowOpacity: 0.1,
          shadowRadius: 12,
          elevation: 8,
        },
        headerShown: false,
      })}
    >
      <Tab.Screen 
        name="Insights" 
        component={HomeScreen} 
        options={{ title: 'Insights' }}
      />
      <Tab.Screen 
        name="Camera" 
        component={CameraScreen} 
        options={{ 
          title: 'Scan'
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen} 
        options={{ title: 'Profile' }}
      />
    </Tab.Navigator>
  );
}

function AuthStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen 
        name="Register" 
        component={RegisterScreen} 
        options={{
          headerShown: false,
        }}
      />
    </Stack.Navigator>
  );
}

function AppNavigator() {
  const { user, isLoading, isGuest } = useAuth();

  if (isLoading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        {/* You can add a loading spinner here */}
      </View>
    );
  }

  // If user is not logged in and not a guest, show auth stack
  if (!user && !isGuest) {
    return <AuthStack />;
  }

  // If user is logged in or is a guest, show main app
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="MainTabs" component={MainTabs} />
      <Stack.Screen 
        name="Analysis" 
        component={AnalysisScreen} 
        options={{
          headerShown: false,
        }}
      />
      <Stack.Screen 
        name="Register" 
        component={RegisterScreen} 
        options={{
          headerShown: false,
        }}
      />
    </Stack.Navigator>
  );
}

function AppContent() {
  const { isDark } = useTheme();
  const colors = getThemeColors(isDark);
  
  return (
    <AuthProvider>
      <AnalysisProvider>
        <NavigationContainer>
          <View style={[styles.container, { backgroundColor: colors.background }]}>
            <StatusBar style={isDark ? "light" : "dark"} />
            <AppNavigator />
          </View>
        </NavigationContainer>
      </AnalysisProvider>
    </AuthProvider>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: Colors.background,
  },
});