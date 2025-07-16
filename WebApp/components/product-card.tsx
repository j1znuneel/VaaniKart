"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import { Plus, Minus } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { Product } from "@/types/product"

interface ProductCardProps {
  product: Product
  dict: Record<string, string> // Dictionary for translations
  getUnitText: (unit: string, quantity: number, dict: Record<string, string>) => string // Corrected signature
  addToCart: (product: Product, quantityToAdd: number) => void
}

export function ProductCard({ product, dict, getUnitText, addToCart }: ProductCardProps) {
  const [selectedQuantity, setSelectedQuantity] = useState(1)

  useEffect(() => {
    // Reset quantity if stock becomes 0 or less than selected
    if (product.current_stock === 0 && selectedQuantity > 0) {
      setSelectedQuantity(0)
    } else if (selectedQuantity > product.current_stock) {
      setSelectedQuantity(product.current_stock)
    } else if (selectedQuantity === 0 && product.current_stock > 0) {
      setSelectedQuantity(1) // Default to 1 if stock becomes available
    }
  }, [product.current_stock, selectedQuantity])

  return (
    <Card className="hover:shadow-xl transition-all duration-300 border-2 border-gray-100 hover:border-green-200 group">
      <CardContent className="p-0">
        <div className="relative overflow-hidden">
          <Image
            src={product.image || "/placeholder.svg?height=200&width=300"}
            alt={product.name}
            width={300}
            height={200}
            className="w-full h-36 sm:h-48 object-cover rounded-t-lg group-hover:scale-105 transition-transform duration-300"
          />
          {product.organic && (
            <Badge className="absolute top-2 right-2 bg-green-600 text-xs shadow-md">{dict.organic}</Badge>
          )}
          <Badge
            className={`absolute top-2 left-2 text-xs shadow-md ${
              product.current_stock > 0 ? "bg-blue-600" : "bg-red-600"
            }`}
          >
            {product.current_stock > 0 ? dict.inStock : dict.outOfStock}
          </Badge>
        </div>
        <div className="p-3 sm:p-4">
          <h3 className="font-semibold text-base sm:text-lg mb-1 text-gray-800 line-clamp-2">{product.name}</h3>
          <p className="text-xs sm:text-sm text-gray-600 mb-3 line-clamp-2">{product.description}</p>
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-3 sm:mb-4 gap-1 sm:gap-0">
            <div>
              <span className="text-lg sm:text-2xl font-bold text-green-600">
                ₹{(product.price * selectedQuantity).toFixed(2)}
              </span>
              <span className="text-gray-500 ml-1 text-sm">
                {getUnitText(product.unit || "kg", selectedQuantity, dict)} {/* Pass dict here */}
              </span>
            </div>
            <span className="text-xs sm:text-sm text-gray-500">
              {product.current_stock} {product.unit || "kg"} {dict.available}
            </span>
          </div>

          {/* Quantity Selector */}
          <div className="flex items-center justify-center space-x-2 mb-3">
            <Button
              size="sm"
              variant="outline"
              onClick={() => setSelectedQuantity((prev) => Math.max(1, prev - 1))}
              disabled={selectedQuantity <= 1 || product.current_stock === 0}
              className="w-8 h-8 p-0"
            >
              <Minus className="w-4 h-4" />
            </Button>
            <Input
              type="number"
              value={selectedQuantity}
              onChange={(e) => {
                const val = Number.parseInt(e.target.value)
                if (!isNaN(val) && val >= 1 && val <= product.current_stock) {
                  setSelectedQuantity(val)
                } else if (e.target.value === "") {
                  setSelectedQuantity(1) // Default to 1 if input is cleared
                }
              }}
              min={1}
              max={product.current_stock}
              className="w-16 text-center text-base font-semibold"
              disabled={product.current_stock === 0}
            />
            <Button
              size="sm"
              variant="outline"
              onClick={() => setSelectedQuantity((prev) => Math.min(product.current_stock, prev + 1))}
              disabled={selectedQuantity >= product.current_stock || product.current_stock === 0}
              className="w-8 h-8 p-0"
            >
              <Plus className="w-4 h-4" />
            </Button>
          </div>

          <Button
            onClick={() => addToCart(product, selectedQuantity)}
            disabled={product.current_stock === 0 || selectedQuantity === 0}
            className="w-full bg-green-600 hover:bg-green-700 text-white py-2 sm:py-3 text-sm sm:text-lg font-medium disabled:bg-gray-400 transition-all duration-200 shadow-md hover:shadow-lg"
          >
            {dict.addToCart}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
