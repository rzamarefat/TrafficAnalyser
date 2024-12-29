import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom"
import { Provider } from 'react-redux'
import Store from './redux/store'

import StreamPage from "./pages/StreamPage"


const App = () => {
    return (
        <Provider store={Store}>
            <Router>
                <Routes>
                    <Route path="/" element={<StreamPage />} />
                </Routes>
            </Router>
        </Provider>
        
        
    )
}


export default App