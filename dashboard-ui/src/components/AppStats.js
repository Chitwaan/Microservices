import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [eventLogStats, setEventLogStats] = useState({});
    const [error, setError] = useState(null);

    const getStats = () => {
        Promise.all([
            fetch(`http://microservices-3855.eastus.cloudapp.azure.com/processing/stats`).then(res => res.json()),
            fetch(`http://microservices-3855.eastus.cloudapp.azure.com:8120/events_stats`).then(res => res.json())
        ])
        .then(([statsResult, eventLogResult]) => {
            console.log("Received Stats and Event Log Stats");
            setStats(statsResult);
            setEventLogStats(eventLogResult);
            setIsLoaded(true);
        },(error) =>{
            setError(error);
            setIsLoaded(true);
        })
    }

    useEffect(() => {
        const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
        return() => clearInterval(interval);
    }, []);

    if (error) {
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (!isLoaded) {
        return(<div>Loading...</div>)
    } else {
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
                    <tbody>
                        <tr>
                            <th>Total Health Metrics</th>
                            <th>Total Workout Events</th>
                            <th>Max Heart Rate</th>
                            <th>Total Calories Burned</th>
                            <th>Total Duration (mins)</th>
                        </tr>
                        <tr>
                            <td>{stats.num_health_metrics}</td>
                            <td>{stats.num_workout_events}</td>
                            <td>{stats.max_heart_rate}</td>
                            <td>{stats.total_calories_burned}</td>
                            <td>{stats.total_duration}</td>
                        </tr>
                    </tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>
                <h2>Event Log Stats</h2>
                {Object.keys(eventLogStats).map(code => (
                    <p key={code}>{code} Events Logged: {eventLogStats[code]}</p>
                ))}
            </div>
        )
    }
}
