import { Inter } from "next/font/google";
import "./globals.css";
import Image from "next/image";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "VP Scraper",
  description: "Scrape product from vistaprint and load it to woocommerce",
};

export default function RootLayout({ children }) {
  return (
    <html lang='en'>
      <body className={`${inter.className} px-20`}>
        <nav className=' py-12 flex justify-start items-center'>
          <a href='/' className='text-white text-lg font-semibold'>
            <Image
              src='./logo.svg'
              alt='Logo'
              className='h-8 mr-2'
              width={100}
              height={50}
            />
          </a>
        </nav>
        <div className='{inter.className}'>{children}</div>
      </body>
    </html>
  );
}
