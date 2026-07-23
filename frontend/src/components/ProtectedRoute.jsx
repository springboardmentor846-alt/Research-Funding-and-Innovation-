import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function ProtectedRoute({ children }) {

    const {authenticated,loading}=useAuth();

    if(loading){
        return <div className="text-center mt-5">Loading...</div>;
    }

    if(!authenticated){
        return <Navigate to="/" replace />;
    }

    return children;
}

export default ProtectedRoute;