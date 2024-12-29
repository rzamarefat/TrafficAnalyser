import React from 'react';
import { Route, Switch, Link } from 'react-router-dom';

const Navbar = () => {
    return (
        <>
            <nav class="navbar navbar-expand-lg navbar-light bg-light">
                <div className='container'>
                        <Link to="/" className='navbar-brand '>Traffic Analyser</Link>
                        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                            <span class="navbar-toggler-icon"></span>
                        </button>
                        <div class="collapse navbar-collapse" id="navbarNav">
                        </div>
                </div>
            </nav>
            
        </>
    )
}

export default Navbar