import './App.css';
import './index.css';
import {BrowserRouter, Route, Routes} from 'react-router-dom';
import {RootPage} from './(root)/RootPage.tsx';

function App() {
    
    return <BrowserRouter>
        <Routes>
            <Route path="/" element={<RootPage/>}/>
        </Routes>
    </BrowserRouter>;
}

export default App;
