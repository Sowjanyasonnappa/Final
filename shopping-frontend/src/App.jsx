import { Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Products from './pages/Products';
import ProductDetails from './pages/ProductDetails';
import Cart from './pages/Cart';
import Orders from './pages/Orders';
import Profile from './pages/Profile';
import AdminDashboard from './pages/AdminDashboard';
import OpsDashboard from './pages/OpsDashboard';
import Settings from './pages/Settings';
import Support from './pages/Support';
import AccessDenied from './pages/AccessDenied';
import NotFound from './pages/NotFound';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import AdminRoute from './components/AdminRoute';
import './styles.css';

function AppRoutes() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-transparent">
      {user ? <Sidebar /> : null}
      <div className={user ? 'lg:pl-65' : ''}>
        <Navbar />
        <main className="min-h-[calc(100vh-5rem)]">
          <Routes>
            <Route path="/" element={<ProtectedRoute><Home /></ProtectedRoute>} />
            <Route path="/login" element={user ? <Navigate to="/products" replace /> : <Login />} />
            <Route path="/register" element={user ? <Navigate to="/products" replace /> : <Register />} />
            <Route path="/products" element={<ProtectedRoute><Products /></ProtectedRoute>} />
            <Route path="/products/:id" element={<ProtectedRoute><ProductDetails /></ProtectedRoute>} />
            <Route path="/cart" element={<ProtectedRoute><Cart /></ProtectedRoute>} />
            <Route path="/orders" element={<ProtectedRoute><Orders /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
            <Route path="/support" element={<ProtectedRoute><Support /></ProtectedRoute>} />
            <Route path="/admin" element={<AdminRoute><AdminDashboard /></AdminRoute>} />
            <Route path="/ops" element={<AdminRoute><OpsDashboard /></AdminRoute>} />
            <Route path="/access-denied" element={<ProtectedRoute><AccessDenied /></ProtectedRoute>} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}