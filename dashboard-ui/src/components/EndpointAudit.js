import React, { useEffect, useState,  useCallback } from 'react'
import '../App.css';

export default function EndpointAudit(props) {
    const [isLoaded, setIsLoaded] = useState(false);
    const [log, setLog] = useState(null);
    const [error, setError] = useState(null)
    const [index, setIndex] = useState(null); 
	// const rand_val = Math.floor(Math.random() * 100); // Get a random event from the event store

    const getAudit = useCallback(() => {
        const rand_val = Math.floor(Math.random() * 100); // Get a random event index
        fetch(`http://microservices-3855.eastus.cloudapp.azure.com:audit_log/${props.endpoint}?index=${rand_val}`)
            .then(res => res.json())
            .then((result) => {
                console.log("Received Audit Results for " + props.endpoint);
                setLog(result);
                setIsLoaded(true);
                setIndex(rand_val); // Set index here to ensure synchronization
            }, (error) => {
                setError(error);
                setIsLoaded(true);
            });
    }, [props.endpoint]);

	useEffect(() => {
		const interval = setInterval(() => getAudit(), 4000); // Update every 4 seconds
		return() => clearInterval(interval);
    }, [getAudit]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        
        return (
            <div>
                <h3>{props.endpoint}-{index}</h3>
                {JSON.stringify(log)}
            </div>
        )
    }
}
