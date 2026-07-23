import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function AdminRoute({ children }) {
  const { user, loading } = useAuth();

  if (loading) return <div className="page">Loading...</div>;
  if (!user || user.role !== 'ADMIN') return <Navigate to="/products" replace />;
  return children;
}