import { useDispatch, useSelector } from "react-redux"

import { Increment, Decrement } from "../redux/actions"


const ComponentA = () => {
    const value = useSelector(state => state.initialValue)
    const dispatch = useDispatch()

    return (
        <>
            <h1>Component A: </h1>
            <h3>The value {value}</h3>
            <button onClick={() => dispatch(Increment())}>Increment</button>
            <button onClick={() => dispatch(Decrement())}>Decrement</button>
        </>
    )
}

export default ComponentA