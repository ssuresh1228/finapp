'use client'
import React, { useEffect, useState } from 'react';
import { ResetPasswordData } from './type';
import styles from './ResetPasswordForm.module.css'
import { useSearchParams, useRouter } from 'next/navigation';

/*
    1. import typescript data structure
    2. useState to instantiate schema
    3. pass structure into component as a prop and access its fields
*/

// gets reset password token from backend and sends to back to /auth/verify
const ResetPasswordForm = () => {
    const router = useRouter();
    const searchParams = useSearchParams()
    const endpoint = 'http://localhost:8000/auth/reset-password'
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{5,}$/;
    //create react component with useState
    const[resetPasswordData, setResetPasswordData] = useState<ResetPasswordData>({
        new_password: '',
        confirm_password: '',
        reset_token: '',
    })
    const [hasMinLength, setHasMinLength] = useState(false);
    const [hasUpper, setHasUpper] = useState(false);
    const [hasLower, setHasLower] = useState(false);
    const [hasNumber, setHasNumber] = useState(false);
    const token = searchParams.get("reset_token")
    const [errorMessage, setErrorMessage] = useState('')
    
    //realtime feedback for meeting password requirements
    const showPasswordTarget = (e: React.ChangeEvent<HTMLInputElement>) => {
        
        const value = e.target.value;
        
        setResetPasswordData({ ...resetPasswordData, new_password: value });
    
        setHasMinLength(value.length >= 5);
        setHasUpper(/[A-Z]/.test(value));
        setHasLower(/[a-z]/.test(value));
        setHasNumber(/\d/.test(value));
    };
    
    // get the token when component mounts
    useEffect(() => {
        if (token) {
            setResetPasswordData(prevData => ({ ...prevData, reset_token: token }));
        }
    }, [token]);    

    //get reset token, validate password then send new password/confirmation to backend 
    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        
        // check if the token is valid 
        if(!token) {
            setErrorMessage("Error - token is invalid or has expired. Send another request to reset your password.")
            return; // kill if token isn't valid
        }
        
        //kill function if password != confirm password 
        if(resetPasswordData.new_password !== resetPasswordData.confirm_password) {
            setErrorMessage("Passwords do not match")
            return; //kill function if not matching
        }
        
        //kill function if password doesn't meet requirements 
        if(!passwordRegex.test(resetPasswordData.new_password)) {
            setErrorMessage("Error - password does not meet requirements")
        }

        // try to send user's data to backend
        try {
            const response = await fetch(endpoint, {
                method:'POST',
                headers: {'content-type':'application/json'},
                //send body as json
                body: JSON.stringify(resetPasswordData)
            });
            
            // go to login on success
            if(response.ok) {
                alert("Your password has been reset, rerouting to login page")
                router.push("/auth/login")
            } else {
                const errorResponse = await response.json()
                alert(errorResponse.detail || "Error: token is invalid or expired.");
            }

        } catch(error) {
            //TODO: better error handling
            console.error("request failed: ", error )
        }
    };
    
    //pass structure into component to access fields 
    return (
        <form className={styles.resetForm} onSubmit={handleSubmit}>
            <input 
                className={styles.input}
                type="password"
                name="newPassword"
                placeholder='Enter your new password'
                value={resetPasswordData.new_password}
                onChange={showPasswordTarget}
            />
            <input 
                className={styles.input}
                type="password"
                name="confirmPassword"
                placeholder='Confirm your new password'
                value={resetPasswordData.confirm_password}
                onChange={(e) => setResetPasswordData({ ...resetPasswordData, confirm_password: e.target.value })}
            />
            <button className={styles.button} type='submit'>Confirm</button>
            <div className={styles.passwordRequirements}>
            <div style={{ color: hasMinLength ? 'green' : 'red' }}>At least 5 characters</div>
            <div style={{ color: hasUpper ? 'green' : 'red' }}>At least one uppercase letter</div>
            <div style={{ color: hasLower ? 'green' : 'red' }}>At least one lowercase letter</div>
            <div style={{ color: hasNumber ? 'green' : 'red' }}>At least one number</div>
            </div>
            <div className={styles.errorMessage}>{errorMessage}</div>
        </form>
    );
};
export default ResetPasswordForm