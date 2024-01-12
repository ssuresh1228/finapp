'use client'
import React, { useState } from 'react';
import { ResetPasswordData } from './type';
import styles from './ResetPassword.module.css'
import { useRouter } from 'next/navigation';

/*
    1. import typescript data structure
    2. useState to instantiate schema
    3. pass structure into component as a prop and access its fields
*/

const endpoint = 'http://localhost:8000/auth/reset-password'

const ResetPasswordForm = () => {
    const router = useRouter();
    //create react component with useState
    const[resetPasswordData, setResetPasswordData] = useState<ResetPasswordData>({
        new_password: ''
    }) 

    //send POST request
    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        try {
            const response = await fetch(endpoint, {
                method:'POST',
                headers: {'content-type':'application/json'},
                //send body as json
                body: JSON.stringify(resetPasswordData)
            });
            
            // go to login on success
            if(response.ok) {
                router.push("/auth/login")
            } else {
                throw new Error(`${response.status}`);
            }
            // LOGGING
            const endpointResponse = await response.json();
            console.log(endpointResponse)

        } catch(error) {
            //TODO: better error handling
            console.error("request failed: ", error )
        }
    };

    //pass structure into component to access fields 
    return (
        <form className={styles.resetForm}>
            <input 
                className={styles.input}
                type = "password"
                name="password"
                onChange={(e) => setResetPasswordData({ ...resetPasswordData, new_password: e.target.value })}
            />
            <button className={styles.button} type='submit'>Register</button>
        </form>
    );
};
export default ResetPasswordForm