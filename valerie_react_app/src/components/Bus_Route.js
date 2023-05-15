import React, {useEffect, useState} from 'react';

const BusRoute = (props) => {

    return (
        <div>
        <h3>{props.routeName}</h3>
        {props.etas.map((eta) => (
            <p>{''+eta} Minutes</p>
        ))}
        </div>
    );
}

export default BusRoute;
