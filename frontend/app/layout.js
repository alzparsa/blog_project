import Header from '../components/Header';
import Footer from '../components/Footer';

import "./globals.css";


export default function rootLayout({ children }) {
  return (
   <html lang="en">
      <body>
        <Header />
        <main>
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
} 