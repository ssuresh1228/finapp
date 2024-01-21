import React from 'react';
import Link from 'next/link';
import styles from './homepage.module.css'

export default function Home() {
  return (
    <main>
      <h1 className={styles.title}>Root Page</h1>
      <h1 className= {styles.log}><Link href = "/auth/login">Register/Login</Link></h1>
    </main>
  )
}