'use client'
import React, {useState} from "react";
import { UserLoginData } from "./types";
import styles from './LoginForm.module.css'
import { useRouter } from 'next/navigation';
import Link from 'next/link'


/*
    1. import typescript data structure
    2. useState to instantiate schema
    3. pass structure into component as a prop and access its fields
*/

const endpoint = 'http://localhost:8000/auth/login'

const LoginForm = () => {
    const router = useRouter();
    //create react component with useState - initially blank
    const[userLoginData, setUserLoginData] = useState<UserLoginData>({
        email: '',
        password:''
    });
    
    //send POST request with user data for backend to verify
    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault()
        //attempt to send request
        try {
            const response = await fetch(endpoint, {
                method:'POST',
                headers:{'content-type': 'application/json'},
                body: JSON.stringify(userLoginData)
            });
            // go to root on success
            if(response.ok) {
                alert("login successful - this is just a placeholder to validate implementation works correctly")
                router.push("/")
            } else {
                throw new Error(`${response.status}`);
            }
            
            //LOGGING
            const endpointResponse = await response.json();
            alert(endpointResponse)

        } catch(error) {
            //TODO: better error handling 
            //console.alert("Registration unsuccessful: ", error)
            console.warn("Registration unsuccessful: ", error)
        }
    };

    //pass structure into component to access fields 
    return(
        <div>
        <form className={styles.LoginForm} onSubmit={handleSubmit}>
            <input 
                className={styles.input}
                type="text"
                value={userLoginData.email}
                placeholder="Enter your email address"
                onChange={(e) => setUserLoginData({...userLoginData, email:e.target.value})}
            />
            <input 
                className={styles.input}
                type="password"
                name="password"
                placeholder="Enter your password"
                value={userLoginData.password}
                onChange={(e) => setUserLoginData({...userLoginData, password:e.target.value})}
            />
            <button className={styles.button} type='submit'>Login</button>
        </form>
        
            <Link href="/">
                <h1 className={styles.OutgoingLink}>
                    Go Home
                </h1>
            </Link>
            <Link href="/auth/register">
                <h1 className={styles.OutgoingLink}>
                    Register for an account here
                </h1>
            </Link>
            <Link href="/auth/check_password_token">
                <h1 className={styles.OutgoingLink}>
                    Reset Password
                </h1>
            </Link>
        </div>
    )
}
export default LoginForm;