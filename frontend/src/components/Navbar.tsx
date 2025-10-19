import React from 'react';
import { Link } from 'react-router-dom';

const Navbar: React.FC = () => {
  return (
    <nav className="navbar absolute top-0 left-0 right-0 z-50 p-6">
      <div className="flex justify-end">
        {/* YouTube Playground Button */}
        <Link
          to="/playground"
          className="group flex items-center gap-2 px-5 py-2.5 bg-[#FF0000] hover:bg-[#CC0000] rounded-full shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
        >
          {/* YouTube Icon SVG */}
          <svg
            className="w-6 h-6 fill-white"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
          </svg>
          
          {/* Text */}
          <span className="text-white font-semibold text-sm tracking-wide">
            Playground
          </span>
        </Link>
      </div>
    </nav>
  );
};

export default Navbar; 