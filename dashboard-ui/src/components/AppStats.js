import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://microservices-3855.eastus.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
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

            </div>
        )
    }
}
