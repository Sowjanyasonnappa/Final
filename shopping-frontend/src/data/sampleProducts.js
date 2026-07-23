const sampleProducts = [
  {
    id: 1001,
    name: 'Aurora Headset',
    description: 'Immersive spatial audio with AI noise suppression.',
    price: 249,
    discount: 15,
    rating: 4.8,
    stock: 24,
    category: 'Audio',
    image: 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80',
    images: [
      'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?auto=format&fit=crop&w=900&q=80',
      'https://images.unsplash.com/photo-1518444065439-e933c06ce9cd?auto=format&fit=crop&w=900&q=80'
    ],
    specifications: ['Wireless', '30-hour battery', 'Noise cancelling']
  },
  {
    id: 1002,
    name: 'Nova Smart Display',
    description: 'A premium display for collaboration and focus.',
    price: 399,
    discount: 10,
    rating: 4.7,
    stock: 12,
    category: 'Displays',
    image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80',
    images: [
      'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=900&q=80',
      'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=900&q=80'
    ],
    specifications: ['4K UHD', 'Touch interface', 'Built-in speakers']
  },
  {
    id: 1003,
    name: 'Lumen Backpack',
    description: 'A lightweight travel companion with smart storage.',
    price: 129,
    discount: 8,
    rating: 4.6,
    stock: 38,
    category: 'Travel',
    image: 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80',
    images: [
      'https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80',
      'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80'
    ],
    specifications: ['Water-resistant', 'USB-C charging', 'Laptop sleeve']
  },
  {
    id: 1004,
    name: 'Atlas Keyboard',
    description: 'Tactile switches and a low-profile premium finish.',
    price: 179,
    discount: 12,
    rating: 4.9,
    stock: 18,
    category: 'Peripherals',
    image: 'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80',
    images: [
      'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80',
      'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?auto=format&fit=crop&w=900&q=80'
    ],
    specifications: ['Mechanical', 'RGB lighting', 'Bluetooth']
  },
  {
    id: 1005,
    name: 'Orbit Watch',
    description: 'Precision wellness insights in a sleek silhouette.',
    price: 299,
    discount: 20,
    rating: 4.8,
    stock: 16,
    category: 'Wearables',
    image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80',
    images: [
      'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=900&q=80',
      'https://images.unsplash.com/photo-1546868871-7041f2a55e12?auto=format&fit=crop&w=900&q=80'
    ],
    specifications: ['Health tracking', 'GPS', 'Fast charging']
  },
  {
    id: 1006,
    name: 'Pulse Speaker',
    description: 'Rich room-filling sound with studio-grade clarity.',
    price: 159,
    discount: 9,
    rating: 4.5,
    stock: 29,
    category: 'Audio',
    image: 'https://images.unsplash.com/photo-1518444065439-e933c06ce9cd?auto=format&fit=crop&w=900&q=80',
    images: [
      'https://images.unsplash.com/photo-1518444065439-e933c06ce9cd?auto=format&fit=crop&w=900&q=80',
      'https://images.unsplash.com/photo-1491926626787-62db157af940?auto=format&fit=crop&w=900&q=80'
    ],
    specifications: ['360° sound', 'Voice assistant', 'USB-C']
  },
  {
    id: 1007,
    name: 'Vertex Tablet',
    description: 'Portable power for work, play, and creative ideas.',
    price: 699,
    discount: 18,
    rating: 4.9,
    stock: 9,
    category: 'Computing',
    image: 'https://images.unsplash.com/photo-1545239351-1141bd82e8a6?auto=format&fit=crop&w=900&q=80',
    images: [
      'https://images.unsplash.com/photo-1545239351-1141bd82e8a6?auto=format&fit=crop&w=900&q=80',
      'https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?auto=format&fit=crop&w=900&q=80'
    ],
    specifications: ['AMOLED display', '128GB', 'Stylus ready']
  },
  {
    id: 1008,
    name: 'Crest Mouse',
    description: 'Precision control with a sculpted ergonomic body.',
    price: 89,
    discount: 7,
    rating: 4.4,
    stock: 31,
    category: 'Peripherals',
    image: 'https://images.unsplash.com/photo-1527814050087-3793815479db?auto=format&fit=crop&w=900&q=80',
    images: [
      'https://images.unsplash.com/photo-1527814050087-3793815479db?auto=format&fit=crop&w=900&q=80',
      'https://images.unsplash.com/photo-1516321497487-e288fb19713f?auto=format&fit=crop&w=900&q=80'
    ],
    specifications: ['Ergonomic', 'Ultra-low latency', 'Rechargeable']
  },
  {
    id: 1009,
    name: 'Halo Camera',
    description: 'A compact creator camera designed for cinematic capture.',
    price: 549,
    discount: 13,
    rating: 4.7,
    stock: 11,
    category: 'Photography',
    image: 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=900&q=80',
    images: [
      'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?auto=format&fit=crop&w=900&q=80',
      'https://images.unsplash.com/photo-1495707902641-75cac588d2e9?auto=format&fit=crop&w=900&q=80'
    ],
    specifications: ['4K video', 'Stabilization', 'Compact body']
  },
  {
    id: 1010,
    name: 'Echo Lamp',
    description: 'Ambient lighting with adaptive warm and cool tones.',
    price: 119,
    discount: 6,
    rating: 4.5,
    stock: 22,
    category: 'Home',
    image: 'https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=900&q=80',
    images: [
      'https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=900&q=80',
      'https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=900&q=80'
    ],
    specifications: ['Adaptive brightness', 'Voice controls', 'App support']
  },
  {
    id: 1011,
    name: 'Summit Bottle',
    description: 'Innovative insulation for workdays and weekends.',
    price: 69,
    discount: 5,
    rating: 4.6,
    stock: 40,
    category: 'Lifestyle',
    image: 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=80',
    images: [
      'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=80',
      'https://images.unsplash.com/photo-1517705008128-361805f42e86?auto=format&fit=crop&w=900&q=80'
    ],
    specifications: ['24-hour insulation', 'Leak-proof', 'Sleek finish']
  },
  {
    id: 1012,
    name: 'Flux Drone',
    description: 'A compact aerial camera with intelligent flight modes.',
    price: 849,
    discount: 16,
    rating: 4.8,
    stock: 7,
    category: 'Photography',
    image: 'https://images.unsplash.com/photo-1473968512647-3e447244af8f?auto=format&fit=crop&w=900&q=80',
    images: [
      'https://images.unsplash.com/photo-1473968512647-3e447244af8f?auto=format&fit=crop&w=900&q=80',
      'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=900&q=80'
    ],
    specifications: ['4K camera', 'Obstacle sensing', 'Flight time 35 min']
  }
];

export default sampleProducts;
