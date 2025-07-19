import './App.css';
import './index.css';
import {BrowserRouter, Route, Routes, useLocation} from 'react-router-dom';
import {RootPage} from './(root)/RootPage.tsx';
import {MainWrapper} from './Main/MainWrapper.tsx';
import {AnimatePresence} from 'framer-motion';

function AppRoutes() {
    const location = useLocation();
    
    return (
        <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
                <Route path="/" element={<RootPage/>}/>
                <Route path="/main" element={<MainWrapper/>}/>
            </Routes>
        </AnimatePresence>
    );
}

function App() {
    
    return <BrowserRouter>
        <AppRoutes/>
    </BrowserRouter>;
}

export default App;
