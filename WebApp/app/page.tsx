"use client"

import { useState, useRef, useEffect } from "react"
import { ShoppingCart, Search, ChevronDown, Languages, RefreshCw, AlertCircle, Minus, Plus, X } from "lucide-react"
import Image from "next/image"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { ProductCard } from "@/components/product-card" // Import the new ProductCard component
import type { Product, CartItem } from "@/types/product" // Import Product and CartItem types

// Comprehensive language dictionaries (simulating Google Translate API)
const dictionaries = {
  en: {
    siteName: "VaaniKart",
    tagline: "Fresh from Farm to Your Home",
    search: "Search products...",
    categories: "Categories",
    cart: "Cart",
    addToCart: "Add to Cart",
    removeFromCart: "Remove",
    updateQuantity: "Update Quantity",
    quantity: "Quantity",
    total: "Total",
    subtotal: "Subtotal",
    checkout: "Proceed to Checkout",
    emptyCart: "Your cart is empty",
    continueShopping: "Continue Shopping",
    perKg: "per kg",
    perLiter: "per liter",
    perPiece: "per piece",
    freshVegetables: "Fresh Vegetables",
    fruits: "Fruits",
    grains: "Grains & Cereals",
    spices: "Spices",
    dairy: "Dairy Products",
    organic: "Organic",
    language: "Language",
    inStock: "In Stock",
    outOfStock: "Out of Stock",
    addedToCart: "Added to Cart!",
    removedFromCart: "Removed from Cart!",
    items: "items",
    item: "item",
    allProducts: "All Products",
    available: "available",
    noResults: "No products found",
    clearSearch: "Clear Search",
    translateWith: "Powered by Translation",
    selectLanguage: "Select Language",
    translating: "Translating...",
    searchResults: "Search Results",
    loading: "Loading products...",
    error: "Error loading products",
    retry: "Retry",
    refreshProducts: "Refresh Products",
    connectionError: "Connection Error",
    serverError: "Server Error",
  },
  hi: {
    siteName: "वाणीकार्ट",
    tagline: "खेत से सीधे आपके घर तक",
    search: "उत्पाद खोजें...",
    categories: "श्रेणियां",
    cart: "कार्ट",
    addToCart: "कार्ट में डालें",
    removeFromCart: "हटाएं",
    updateQuantity: "मात्रा बदलें",
    quantity: "मात्रा",
    total: "कुल राशि",
    subtotal: "उप-योग",
    checkout: "चेकआउट पर जाएं",
    emptyCart: "आपका कार्ट खाली है",
    continueShopping: "खरीदारी जारी रखें",
    perKg: "प्रति किलो",
    perLiter: "प्रति लीटर",
    perPiece: "प्रति पीस",
    freshVegetables: "ताज़ी सब्जियां",
    fruits: "फल",
    grains: "अनाज और दालें",
    spices: "मसाले",
    dairy: "डेयरी उत्पाद",
    organic: "जैविक",
    language: "भाषा",
    inStock: "स्टॉक में उपलब्ध",
    outOfStock: "स्टॉक समाप्त",
    addedToCart: "कार्ट में जोड़ा गया!",
    removedFromCart: "कार्ट से हटाया गया!",
    items: "वस्तुएं",
    item: "वस्तु",
    allProducts: "सभी उत्पाद",
    available: "उपलब्ध",
    noResults: "कोई उत्पाद नहीं मिला",
    clearSearch: "खोज साफ़ करें",
    translateWith: "अनुवाद द्वारा संचालित",
    selectLanguage: "भाषा चुनें",
    translating: "अनुवाद हो रहा है...",
    searchResults: "खोज परिणाम",
    loading: "उत्पाद लोड हो रहे हैं...",
    error: "उत्पाद लोड करने में त्रुटि",
    retry: "पुनः प्रयास करें",
    refreshProducts: "उत्पाद रीफ्रेश करें",
    connectionError: "कनेक्शन त्रुटि",
    serverError: "सर्वर त्रुटि",
  },
  ta: {
    siteName: "வாணிகார்ட்",
    tagline: "வயலில் இருந்து நேரடியாக உங்கள் வீட்டிற்கு",
    search: "பொருட்களைத் தேடுங்கள்...",
    categories: "வகைகள்",
    cart: "கார்ட்",
    addToCart: "கார்ட்டில் சேர்க்க",
    removeFromCart: "அகற்று",
    updateQuantity: "அளவை மாற்று",
    quantity: "அளவு",
    total: "மொத்த தொகை",
    subtotal: "துணை மொத்தம்",
    checkout: "செக்அவுட்டிற்கு செல்லவும்",
    emptyCart: "உங்கள் கார்ட் காலியாக உள்ளது",
    continueShopping: "ஷாப்பிங் தொடரவும்",
    perKg: "ஒரு கிலோ",
    perLiter: "ஒரு லிட்டர்",
    perPiece: "ஒரு துண்டு",
    freshVegetables: "புதிய காய்கறிகள்",
    fruits: "பழங்கள்",
    grains: "தானியங்கள் மற்றும் பருப்புகள்",
    spices: "மசாலாப் பொருட்கள்",
    dairy: "பால் பொருட்கள்",
    organic: "இயற்கை",
    language: "மொழி",
    inStock: "கையிருப்பில் உள்ளது",
    outOfStock: "கையிருப்பு இல்லை",
    addedToCart: "கார்ட்டில் சேர்க்கப்பட்டது!",
    removedFromCart: "கார்ட்டில் இருந்து அகற்றப்பட்டது!",
    items: "பொருட்கள்",
    item: "பொருள்",
    allProducts: "அனைத்து பொருட்கள்",
    available: "கிடைக்கிறது",
    noResults: "பொருட்கள் எதுவும் கிடைக்கவில்லை",
    clearSearch: "தேடலை அழிக்கவும்",
    translateWith: "மொழிபெயர்ப்பால் இயக்கப்படுகிறது",
    selectLanguage: "மொழியைத் தேர்ந்தெடுக்கவும்",
    translating: "மொழிபெயர்க்கிறது...",
    searchResults: "தேடல் முடிவுகள்",
    loading: "பொருட்கள் ஏற்றப்படுகின்றன...",
    error: "பொருட்களை ஏற்றுவதில் பிழை",
    retry: "மீண்டும் முயற்சிக்கவும்",
    refreshProducts: "பொருட்களை புதுப்பிக்கவும்",
    connectionError: "இணைப்பு பிழை",
    serverError: "சர்வர் பிழை",
  },
}

// Categories mapping for UI (names are translated via dictionaries)
const categories = [
  {
    id: "vegetables",
    icon: "🥬",
    name: {
      en: "Fresh Vegetables",
      hi: "ताज़ी सब्जियां",
      ta: "புதிய காய்கறிகள்",
    },
  },
  {
    id: "fruits",
    icon: "🍎",
    name: {
      en: "Fruits",
      hi: "फल",
      ta: "பழங்கள்",
    },
  },
  {
    id: "grains",
    icon: "🌾",
    name: {
      en: "Grains & Cereals",
      hi: "अनाज और दालें",
      ta: "தானியங்கள் மற்றும் பருப்புகள்",
    },
  },
  {
    id: "spices",
    icon: "🌶️",
    name: {
      en: "Spices",
      hi: "मसाले",
      ta: "மசாலாப் பொருட்கள்",
    },
  },
  {
    id: "dairy",
    icon: "🥛",
    name: {
      en: "Dairy Products",
      hi: "डेयरी उत्पाद",
      ta: "பால் பொருட்கள்",
    },
  },
]

// API functions
// Update the getProductsFromApi function in your React component
// API function to fetch products from Django
async function getProductsFromApi(): Promise<Product[]> {
  try {
    const res = await fetch("https://remhqhnmphsxufvdpokr.supabase.co/api/products/", {
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
      },
    });
    
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.error || "Failed to fetch products");
    }
    
    const data = await res.json();
    
    // Transform the API response to match frontend expectations
    return data.map((product: any) => ({
      id: product.id,
      name: product.name,
      description: product.description,
      category: product.category,
      price: parseFloat(product.price),
      current_stock: parseInt(product.current_stock),
      image: product.image || "/placeholder.svg?height=200&width=200",
      organic: product.organic || false,
      unit: product.unit || "kg",
    }));
  } catch (error) {
    console.error("Error fetching products:", error);
    throw error;
  }
}

const getUnitText = (unit: string, quantity: number, dict: Record<string, string>) => {
  if (quantity > 1) return "";
  switch (unit) {
    case "kg": return dict.perKg;
    case "liter": return dict.perLiter;
    case "piece": return dict.perPiece;
    default: return `/${unit}`;
  }
}

export default function VaaniKart() {
  const [language, setLanguage] = useState<"en" | "hi" | "ta">("en");
  const [cart, setCart] = useState<CartItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const [notification, setNotification] = useState("");
  const [isTranslating, setIsTranslating] = useState(false);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const searchRef = useRef<HTMLDivElement>(null);
  const dict = dictionaries[language];

  // Fetch products from Django API
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await getProductsFromApi();
        setProducts(data);
      } catch (err) {
        console.error("Error:", err);
        setError(err instanceof Error ? err.message : "Unknown error occurred");
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);
  const fetchProducts = async () => {
    try {
      setLoading(true)
      setError(null)
      const fetchedProducts = await getProductsFromApi()
      setProducts(fetchedProducts)
      console.log(products)
    } catch (err) {
      console.error("Error fetching products:", err)
      setError(err instanceof Error ? err.message : "Unknown error occurred")
      // Fallback to sample data if API fails
      // setProducts(FALLBACK_PRODUCTS)
    } finally {
      setLoading(false)
    }
  }

  // Close search dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowSearchDropdown(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const showNotification = (message: string) => {
    setNotification(message)
    setTimeout(() => setNotification(""), 3000)
  }

  // Simulate translation API call
  const handleLanguageChange = (newLanguage: "en" | "hi" | "ta") => {
    setIsTranslating(true)
    setTimeout(() => {
      setLanguage(newLanguage)
      setIsTranslating(false)
      showNotification(
        `Language changed to ${newLanguage === "en" ? "English" : newLanguage === "hi" ? "हिंदी" : "தமிழ்"}`,
      )
    }, 500)
  }

  const addToCart = (product: Product, quantityToAdd: number) => {
    setCart((prevCart) => {
      const existingItem = prevCart.find((item) => item.id === product.id)
      if (existingItem) {
        return prevCart.map((item) =>
          item.id === product.id ? { ...item, quantity: item.quantity + quantityToAdd } : item,
        )
      } else {
        return [
          ...prevCart,
          {
            id: product.id,
            name: product.name, // Use product.name directly as it's a string from API
            price: product.price,
            quantity: quantityToAdd,
            unit: product.unit || "kg",
            image: product.image,
          },
        ]
      }
    })
    showNotification(dict.addedToCart)
  }

  const removeFromCart = (productId: number) => {
    setCart((prevCart) => prevCart.filter((item) => item.id !== productId))
    showNotification(dict.removedFromCart)
  }

  const updateQuantity = (productId: number, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeFromCart(productId)
      return
    }
    setCart((prevCart) => prevCart.map((item) => (item.id === productId ? { ...item, quantity: newQuantity } : item)))
  }

  const getTotalItems = () => {
    return cart.reduce((total, item) => total + item.quantity, 0)
  }

  const getTotalPrice = () => {
    return cart.reduce((total, item) => total + item.price * item.quantity, 0)
  }

  const filteredProducts = products.filter((product) => {
    const matchesCategory = !selectedCategory || product.category === selectedCategory
    const matchesSearch = !searchTerm || product.name.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesCategory && matchesSearch
  })

  const searchSuggestions = searchTerm
    ? products.filter((product) => product.name.toLowerCase().includes(searchTerm.toLowerCase())).slice(0, 5)
    : []

  const handleSearchSelect = (product: Product) => {
    setSearchTerm(product.name)
    setShowSearchDropdown(false)
    setSelectedCategory(null)
  }

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-green-50 to-white flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-green-600 animate-spin mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-800 mb-2">{dict.siteName}</h2>
          <p className="text-lg text-gray-600">{dict.loading}</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error && products.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-b from-green-50 to-white flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <Alert className="border-red-200 bg-red-50">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <AlertDescription className="text-red-800">
              <strong>{dict.error}:</strong> {error}. {dict.connectionError}.
            </AlertDescription>
          </Alert>
          <div className="mt-6 text-center">
            <Button onClick={fetchProducts} className="bg-green-600 hover:bg-green-700">
              <RefreshCw className="w-4 h-4 mr-2" />
              {dict.retry}
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 to-white">
      {/* Notification */}
      {notification && (
        <div className="fixed top-4 right-4 bg-green-600 text-white px-4 py-3 rounded-lg shadow-lg z-50 animate-in slide-in-from-right max-w-xs">
          <p className="text-sm font-medium">{notification}</p>
        </div>
      )}

      {/* Translation Loading Indicator */}
      {isTranslating && (
        <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white p-6 rounded-lg shadow-xl z-50 flex items-center space-x-3">
          <Languages className="w-6 h-6 text-green-600 animate-pulse" />
          <span className="text-lg font-medium">{dict.translating}</span>
        </div>
      )}

      {/* Header */}
      <header className="bg-white shadow-sm border-b-2 border-green-100 sticky top-0 z-40">
        <div className="container mx-auto px-3 sm:px-4 py-3 sm:py-4">
          <div className="flex items-center justify-between gap-2 sm:gap-4">
            {/* Logo */}
            <div className="flex items-center space-x-2 sm:space-x-3 flex-shrink-0">
              <div className="w-8 h-8 sm:w-12 sm:h-12 bg-green-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-sm sm:text-xl">V</span>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl sm:text-2xl font-bold text-green-800">{dict.siteName}</h1>
                <p className="text-xs sm:text-sm text-green-600">{dict.tagline}</p>
              </div>
            </div>

            {/* Right Side Actions */}
            <div className="flex items-center space-x-2 sm:space-x-4 flex-shrink-0">
              {/* Refresh Button */}
              <Button
                variant="outline"
                size="sm"
                onClick={fetchProducts}
                className="flex items-center space-x-1 bg-transparent px-2 sm:px-3 border-green-300 hover:bg-green-50"
                disabled={loading}
              >
                <RefreshCw className={`w-3 h-3 sm:w-4 sm:h-4 ${loading ? "animate-spin" : ""}`} />
                <span className="hidden sm:inline text-xs sm:text-sm">{dict.refreshProducts}</span>
              </Button>

              {/* Enhanced Language Selector */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex items-center space-x-1 sm:space-x-2 bg-transparent px-2 sm:px-3 border-green-300 hover:bg-green-50"
                    disabled={isTranslating}
                  >
                    <Languages className="w-3 h-3 sm:w-4 sm:h-4 text-green-600" />
                    <span className="hidden sm:inline text-xs sm:text-sm font-medium">
                      {language === "en" ? "EN" : language === "hi" ? "हि" : "त"}
                    </span>
                    <ChevronDown className="w-3 h-3 sm:w-4 sm:h-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem onClick={() => handleLanguageChange("en")} className="flex items-center space-x-2">
                    <span className="font-medium">🇺🇸 English</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleLanguageChange("hi")} className="flex items-center space-x-2">
                    <span className="font-medium">🇮🇳 हिंदी</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => handleLanguageChange("ta")} className="flex items-center space-x-2">
                    <span className="font-medium">🇮🇳 தமிழ்</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Cart */}
              <Sheet>
                <SheetTrigger asChild>
                  <Button
                    variant="outline"
                    className="relative bg-transparent px-2 sm:px-3 border-green-300 hover:bg-green-50"
                  >
                    <ShoppingCart className="w-4 h-4 sm:w-5 sm:h-5 text-green-600" />
                    <span className="ml-1 sm:ml-2 hidden sm:inline text-xs sm:text-sm font-medium">{dict.cart}</span>
                    {getTotalItems() > 0 && (
                      <Badge className="absolute -top-1 -right-1 sm:-top-2 sm:-right-2 bg-red-500 text-xs px-1 min-w-[1.25rem] h-5">
                        {getTotalItems()}
                      </Badge>
                    )}
                  </Button>
                </SheetTrigger>
                <SheetContent className="w-full sm:max-w-lg flex flex-col h-full p-0">
                  <SheetHeader className="p-4 sm:p-6 border-b flex-shrink-0 bg-green-50">
                    <SheetTitle className="text-lg sm:text-xl font-bold text-left text-green-800">
                      {dict.cart} ({getTotalItems()} {getTotalItems() === 1 ? dict.item : dict.items})
                    </SheetTitle>
                  </SheetHeader>

                  {cart.length === 0 ? (
                    <div className="flex-1 flex items-center justify-center p-4">
                      <div className="text-center">
                        <ShoppingCart className="w-12 h-12 sm:w-16 sm:h-16 text-gray-300 mx-auto mb-4" />
                        <p className="text-base sm:text-lg text-gray-500 mb-4">{dict.emptyCart}</p>
                        <Button
                          onClick={() => (document.querySelector("[data-sheet-close]") as HTMLElement | null)?.click()}
                          className="bg-green-600 hover:bg-green-700"
                        >
                          {dict.continueShopping}
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <div className="flex-1 overflow-y-auto">
                        <div className="p-4 sm:p-6 space-y-3 sm:space-y-4">
                          {cart.map((item) => (
                            <div
                              key={item.id}
                              className="flex items-center space-x-3 p-3 sm:p-4 border rounded-lg bg-white shadow-sm"
                            >
                              <Image
                                src={item.image || "/placeholder.svg?height=60&width=60"}
                                alt={item.name}
                                width={50}
                                height={50}
                                className="w-12 h-12 sm:w-16 sm:h-16 rounded-lg object-cover flex-shrink-0"
                              />
                              <div className="flex-1 min-w-0">
                                <h3 className="font-semibold text-sm sm:text-base truncate">{item.name}</h3>
                                <p className="text-green-600 font-bold text-sm sm:text-base">
                                  ₹{item.price.toFixed(2)} {getUnitText(item.unit, 1, dict)}
                                </p>
                                <div className="flex items-center space-x-2 mt-2">
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => updateQuantity(item.id, item.quantity - 1)}
                                    className="w-7 h-7 sm:w-8 sm:h-8 p-0 flex-shrink-0"
                                  >
                                    <Minus className="w-3 h-3 sm:w-4 sm:h-4" />
                                  </Button>
                                  <span className="w-6 sm:w-8 text-center font-semibold text-sm sm:text-base">
                                    {item.quantity}
                                  </span>
                                  <Button
                                    size="sm"
                                    variant="outline"
                                    onClick={() => updateQuantity(item.id, item.quantity + 1)}
                                    className="w-7 h-7 sm:w-8 sm:h-8 p-0 flex-shrink-0"
                                  >
                                    <Plus className="w-3 h-3 sm:w-4 sm:h-4" />
                                  </Button>
                                </div>
                              </div>
                              <div className="text-right flex-shrink-0">
                                <p className="font-bold text-sm sm:text-base">
                                  ₹{(item.price * item.quantity).toFixed(2)}{" "}
                                  {getUnitText(item.unit, item.quantity, dict)}
                                </p>
                                <Button
                                  size="sm"
                                  variant="ghost"
                                  onClick={() => removeFromCart(item.id)}
                                  className="text-red-500 hover:text-red-700 p-1 mt-1"
                                >
                                  <X className="w-3 h-3 sm:w-4 sm:h-4" />
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Fixed Checkout Section */}
                      <div className="border-t bg-white flex-shrink-0">
                        <div className="p-4 sm:p-6">
                          <div className="flex justify-between items-center mb-4">
                            <span className="text-lg sm:text-xl font-bold">{dict.total}:</span>
                            <span className="text-xl sm:text-2xl font-bold text-green-600">
                              ₹{getTotalPrice().toFixed(2)}
                            </span>
                          </div>
                          <Button className="w-full bg-green-600 hover:bg-green-700 text-white py-3 sm:py-4 text-base sm:text-lg font-medium shadow-lg">
                            {dict.checkout}
                          </Button>
                        </div>
                      </div>
                    </>
                  )}
                </SheetContent>
              </Sheet>
            </div>
          </div>

          {/* Enhanced Search Bar */}
          <div className="mt-3 sm:mt-4">
            <div className="relative max-w-md mx-auto" ref={searchRef}>
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 sm:w-5 sm:h-5" />
              <Input
                type="text"
                placeholder={dict.search}
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value)
                  setShowSearchDropdown(e.target.value.length > 0)
                }}
                onFocus={() => setShowSearchDropdown(searchTerm.length > 0)}
                className="pl-10 sm:pl-12 py-2 sm:py-3 text-base sm:text-lg border-2 border-green-200 focus:border-green-500 rounded-lg"
              />

              {/* Enhanced Search Dropdown */}
              {showSearchDropdown && searchSuggestions.length > 0 && (
                <div className="absolute top-full left-0 right-0 bg-white border-2 border-green-200 border-t-0 rounded-b-lg shadow-xl z-50 max-h-60 overflow-y-auto">
                  <div className="p-2 bg-green-50 border-b">
                    <p className="text-xs text-green-700 font-medium">{dict.searchResults}</p>
                  </div>
                  {searchSuggestions.map((product) => (
                    <div
                      key={product.id}
                      onClick={() => handleSearchSelect(product)}
                      className="flex items-center space-x-3 p-3 hover:bg-green-50 cursor-pointer border-b border-gray-100 last:border-b-0 transition-colors"
                    >
                      <Image
                        src={product.image || "/placeholder.svg?height=40&width=40"}
                        alt={product.name}
                        width={40}
                        height={40}
                        className="w-8 h-8 sm:w-10 sm:h-10 rounded object-cover flex-shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm sm:text-base truncate">{product.name}</p>
                        <p className="text-green-600 text-xs sm:text-sm">
                          ₹{product.price.toFixed(2)} {getUnitText(product.unit || "kg", 1, dict)}
                        </p>
                      </div>
                      <div className="flex flex-col items-end space-y-1">
                        {product.organic && <Badge className="bg-green-600 text-xs">Organic</Badge>}
                        <Badge className={`text-xs ${product.current_stock > 0 ? "bg-blue-600" : "bg-red-600"}`}>
                          {product.current_stock > 0 ? dict.inStock : dict.outOfStock}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Categories */}
      <section className="py-4 sm:py-8 bg-white">
        <div className="container mx-auto px-3 sm:px-4">
          <h2 className="text-xl sm:text-2xl font-bold text-center mb-4 sm:mb-8 text-gray-800">{dict.categories}</h2>
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 sm:gap-4">
            <Card
              className={`hover:shadow-lg transition-all duration-200 cursor-pointer border-2 ${
                selectedCategory === null
                  ? "border-green-500 bg-green-50 shadow-md"
                  : "border-green-100 hover:border-green-300"
              }`}
              onClick={() => setSelectedCategory(null)}
            >
              <CardContent className="p-3 sm:p-6 text-center">
                <div className="text-2xl sm:text-4xl mb-1 sm:mb-3">🛒</div>
                <h3 className="font-semibold text-xs sm:text-sm text-gray-800">{dict.allProducts}</h3>
              </CardContent>
            </Card>
            {categories.map((category) => (
              <Card
                key={category.id}
                className={`hover:shadow-lg transition-all duration-200 cursor-pointer border-2 ${
                  selectedCategory === category.id
                    ? "border-green-500 bg-green-50 shadow-md"
                    : "border-green-100 hover:border-green-300"
                }`}
                onClick={() => setSelectedCategory(selectedCategory === category.id ? null : category.id)}
              >
                <CardContent className="p-3 sm:p-6 text-center">
                  <div className="text-2xl sm:text-4xl mb-1 sm:mb-3">{category.icon}</div>
                  <h3 className="font-semibold text-xs sm:text-sm text-gray-800 leading-tight">
                    {category.name[language]}
                  </h3>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Products */}
      <section className="py-6 sm:py-12">
        <div className="container mx-auto px-3 sm:px-4">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 sm:mb-8 gap-2">
            <h2 className="text-xl sm:text-3xl font-bold text-gray-800">
              {selectedCategory ? categories.find((c) => c.id === selectedCategory)?.name[language] : dict.allProducts}
            </h2>
            <div className="text-sm text-gray-600">
              {filteredProducts.length} {filteredProducts.length === 1 ? dict.item : dict.items}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
            {filteredProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                dict={dict}
                getUnitText={getUnitText}
                addToCart={addToCart}
              />
            ))}
          </div>

          {filteredProducts.length === 0 && !loading && (
            <div className="text-center py-8 sm:py-12">
              <Search className="w-12 h-12 sm:w-16 sm:h-16 text-gray-300 mx-auto mb-4" />
              <p className="text-lg sm:text-xl text-gray-500 mb-4">{dict.noResults}</p>
              <Button
                onClick={() => {
                  setSearchTerm("")
                  setSelectedCategory(null)
                  setShowSearchDropdown(false)
                }}
                variant="outline"
                className="bg-white hover:bg-green-50 border-green-300"
              >
                {dict.clearSearch}
              </Button>
            </div>
          )}
        </div>
      </section>

      {/* Translation Attribution */}
      <div className="bg-green-100 py-2">
        <div className="container mx-auto px-3 sm:px-4 text-center">
          <p className="text-xs text-green-700">
            <Languages className="w-3 h-3 inline mr-1" />
            {dict.translateWith}
          </p>
        </div>
      </div>
    </div>
  )
}
// "use client";

// import { useEffect, useState } from "react";
// import { Button } from "@/components/ui/button";
// import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
// import { Badge } from "@/components/ui/badge";
// import { Trash2 } from "lucide-react";

// type Product = {
//   id: number;
//   name: string;
//   description: string;
//   price: number;
//   current_stock: number;
//   category: string;
// };

// type CartItem = {
//   id: number;
//   name: string;
//   price: number;
//   quantity: number;
// };

// export default function Home() {
//   const [products, setProducts] = useState<Product[]>([]);
//   const [error, setError] = useState("");
//   const [cart, setCart] = useState<CartItem[]>([]);

//   useEffect(() => {
//     fetch("http://localhost:8000/api/products/")
//       .then((res) => {
//         if (!res.ok) throw new Error("Failed to fetch");
//         return res.json();
//       })
//       .then((data) => setProducts(data))
//       .catch((err) => setError(err.message));
//   }, []);

//   const addToCart = (product: Product) => {
//     setCart((prev) => {
//       const exists = prev.find((item) => item.id === product.id);
//       if (exists) {
//         return prev.map((item) =>
//           item.id === product.id
//             ? { ...item, quantity: item.quantity + 1 }
//             : item
//         );
//       }
//       return [...prev, { id: product.id, name: product.name, price: product.price, quantity: 1 }];
//     });
//   };

//   const removeFromCart = (id: number) => {
//     setCart((prev) => prev.filter((item) => item.id !== id));
//   };

//   const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

//   return (
//     <main className="min-h-screen bg-gray-50 py-10 px-6">
//       <div className="flex justify-between items-center mb-6">
//         <h1 className="text-3xl font-bold">🛍️ Product Catalog</h1>

//         <Sheet>
//           <SheetTrigger asChild>
//             <Button variant="outline">
//               🛒 Cart <Badge className="ml-2">{cart.length}</Badge>
//             </Button>
//           </SheetTrigger>
//           <SheetContent side="right" className="w-[350px]">
//             <h2 className="text-xl font-bold mb-4">🧺 Your Cart</h2>
//             {cart.length === 0 ? (
//               <p className="text-sm text-gray-500">Cart is empty</p>
//             ) : (
//               <div className="space-y-4">
//                 {cart.map((item) => (
//                   <div
//                     key={item.id}
//                     className="flex justify-between items-center border-b pb-2"
//                   >
//                     <div>
//                       <p className="font-semibold">{item.name}</p>
//                       <p className="text-sm text-gray-500">
//                         ₹{item.price} x {item.quantity}
//                       </p>
//                     </div>
//                     <Button
//                       size="icon"
//                       variant="ghost"
//                       onClick={() => removeFromCart(item.id)}
//                     >
//                       <Trash2 className="w-4 h-4 text-red-500" />
//                     </Button>
//                   </div>
//                 ))}
//                 <div className="pt-4 border-t font-semibold">
//                   Total: ₹{total.toFixed(2)}
//                 </div>
//                 <Button className="w-full bg-green-600 hover:bg-green-700">
//                   Proceed to Checkout
//                 </Button>
//               </div>
//             )}
//           </SheetContent>
//         </Sheet>
//       </div>

//       {error && <p className="text-red-500 text-center">{error}</p>}

//       <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
//         {products.map((product) => (
//           <div key={product.id} className="bg-white rounded-xl shadow p-4">
//             <h2 className="text-xl font-semibold mb-1">{product.name}</h2>
//             <p className="text-sm text-gray-600 mb-2">{product.description}</p>
//             <p className="text-md font-medium">💰 ₹{product.price}</p>
//             <p className="text-sm text-gray-700">📦 Stock: {product.current_stock}</p>
//             <p className="text-sm text-gray-500 mb-3">🏷️ {product.category}</p>
//             <Button
//               onClick={() => addToCart(product)}
//               disabled={product.current_stock <= 0}
//               className="w-full bg-blue-600 hover:bg-blue-700"
//             >
//               {product.current_stock > 0 ? "Add to Cart" : "Out of Stock"}
//             </Button>
//           </div>
//         ))}
//       </div>

//       {!products.length && !error && (
//         <p className="text-center text-gray-500 mt-8">Loading products...</p>
//       )}
//     </main>
//   );
// }
