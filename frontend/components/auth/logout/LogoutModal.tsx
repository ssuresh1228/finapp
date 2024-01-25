import React from "react";
import styles from './LogoutButton.module.css'

// asks the user if they want to log out or not

interface LogoutModal {
    isModalOpen: boolean;
    onConfirm: () => void;
    onCancel: () => void; 
}

const LogoutModal: React.FC<LogoutModal> = ({isModalOpen, onConfirm, onCancel}) => {
    //return null if not open to do nothing 
    if(!isModalOpen) return null; 

    //creates the popup
    return (
        <div>
            <p>Are you sure you want to log out?</p>
            <button onClick={onConfirm} className={styles.button}>Yes</button>
            <button onClick={onCancel} className={styles.button}>No</button>
        </div>
    );
};
export default LogoutModal;