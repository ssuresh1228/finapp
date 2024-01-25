'use client'
import React, {useState, useContext } from "react";
import LogoutModal from "./LogoutModal";
import { UserAuthContext, useUserAuth } from "@/contexts/UserAuthContext";
import { useRouter } from "next/navigation";
import styles from './LogoutButton.module.css';

const LogoutButton = () => {
    // init modal with false initial state
    const[isModalVisible, setIsModalVisible] = useState(false)
    const router = useRouter();
    const { logout } = useContext(UserAuthContext)
    const endpoint = "http://localhost:8000/auth/logout"

    //send request to endpoint 
    const handleUserLogoutConfirmation = async () => {
        try {
            const response = await fetch (endpoint, {
                method: "POST",
                credentials: "include",
            })
            
            //if backend returns 200 OK, reset user state and reroute to login 
            if(response.ok) {
                logout();
                router.push('/auth/login')
            }
            else {
                console.error("Logout failed");
            }
        }
        catch (error){
            console.log("Error occurred during logout: ", error);
        }
        //close the modal 
        setIsModalVisible(false);
    };

    return (
        <div>
            <button onClick={() => setIsModalVisible(true)} className={styles.button}>Logout</button>
            <LogoutModal
                isModalOpen={isModalVisible}
                onConfirm = {handleUserLogoutConfirmation}
                onCancel = {() => setIsModalVisible(false)}
            />
        </div>
    )
}
export default LogoutButton;