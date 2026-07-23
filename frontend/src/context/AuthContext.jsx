import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/api";

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {

    const [user,setUser]=useState(null);
    const [loading,setLoading]=useState(true);

    useEffect(()=>{

        const token=localStorage.getItem("token");

        if(!token){
            setLoading(false);
            return;
        }

        api.get("/auth/me")
        .then(res=>{
            setUser(res.data);
        })
        .catch(()=>{
            localStorage.removeItem("token");
            setUser(null);
        })
        .finally(()=>{
            setLoading(false);
        });

    },[]);

    const login=async(email,password)=>{

        const form=new URLSearchParams();

        form.append("username",email);
        form.append("password",password);

        const res=await api.post("/auth/login",form,{
            headers:{
                "Content-Type":"application/x-www-form-urlencoded"
            }
        });

        localStorage.setItem("token",res.data.access_token);

        const me=await api.get("/auth/me");

        setUser(me.data);

    };

    const register=async(data)=>{
        await api.post("/auth/register",data);
    };

    const logout=()=>{
        localStorage.removeItem("token");
        setUser(null);
    };

    return(
        <AuthContext.Provider value={{
            user,
            login,
            logout,
            register,
            loading,
            authenticated:!!user
        }}>
            {children}
        </AuthContext.Provider>
    );

}