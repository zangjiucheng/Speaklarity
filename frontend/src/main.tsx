import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import './index.css';
import App from './App.tsx';
import {HeroUIProvider} from '@heroui/react';
import {Toaster} from 'react-hot-toast';

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <Toaster />
        <HeroUIProvider>
            <App/>
        </HeroUIProvider>
    </StrictMode>,
);
