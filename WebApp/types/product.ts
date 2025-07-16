// Django API Product interface
export interface Product {
  id: number
  name: string
  description: string
  category: string
  price: number
  current_stock: number
  image?: string
  organic?: boolean
  unit?: string
}

export interface CartItem {
  id: number
  name: string
  price: number
  quantity: number
  unit: string
  image?: string
}
