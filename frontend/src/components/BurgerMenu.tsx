import React, { useState } from "react";
interface MenuItem {
  label: string;
  href: string;
}

interface BurgerMenuProps {
  items: MenuItem[];
}

const BurgerMenu: React.FC<BurgerMenuProps> = ({ items }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => setIsOpen(!isOpen);
  const closeMenu = () => setIsOpen(false);

  return (
    <>
      <button
        className="btn d-lg-none"
        onClick={toggleMenu}
        aria-label="Abrir menú"
      >
        <img src="/src/assets/menu.png" alt="menu" height={16} width={16} />
      </button>

      {isOpen && <div className="menu-overlay" onClick={closeMenu}></div>}

      <div className={`burger-menu ${isOpen ? "open" : ""}`}>
        <ul className="list-unstyled m-0 p-3">
          {items.map((item, index) => (
            <li key={index} className="mb-2">
              <a
                href={item.href}
                className="text-white text-decoration-none"
                onClick={closeMenu}
              >
                {item.label}
              </a>
            </li>
          ))}
        </ul>
        <div className="text-center mt-5"></div>
      </div>

      {/* Estilos en línea */}
      <style>{`
        .burger-menu {
          position: fixed;
          top: 0;
          right: 0;
          width: 250px;
          height: 100vh;
          background-color: #007bff; 
          box-shadow: -2px 0 5px rgba(0, 0, 0, 0.5);
          transform: translateX(100%);
          transition: transform 0.3s ease-in-out;
          z-index: 1051;
        }

        .burger-menu.open {
          transform: translateX(0);
        }

        .menu-overlay {
          position: fixed;
          top: 0;
          left: 0;
          width: 100vw;
          height: 100vh;
          background-color: rgba(0, 0, 0, 0.5);
          z-index: 1050;
        }
      `}</style>
    </>
  );
};

export default BurgerMenu;
