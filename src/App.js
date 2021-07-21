import './App.css';
import React, { useState, useEffect} from 'react'
import axios from 'axios';
import Coin from './Coin';


function App() {

  const [currencyTag,setCurrencyTag] = useState('usd');

  const [coins,setCoins] = useState([]);
  const [search,setSearch] = useState('');

  useEffect(()=>{

    axios.get(`https://api.coingecko.com/api/v3/coins/markets?vs_currency=${currencyTag}&order=market_cap_desc&per_page=100&page=1&sparkline=true&price_change_percentage=1h%2C24h%2C7d`)
    .then(res => {
      setCoins(res.data);
      console.log(res.data);
    })
    .catch(err => {
      console.error(err.message);
    })

  },[currencyTag]);

  const handleChange = (e) => {
    setSearch(e.target.value);
  }


  const filteredCoins = coins.filter(coin => 
      coin.name.toLowerCase().includes(search.toLowerCase())
    )

  return (
    <div className="coin-app">

      {/* Search Bar */}
      <div className="coin-search">
        <h1 className="coin-text">Search a currency</h1>
        <form>
          <input type="text" placeholder="Search" className="coin-input" onChange={handleChange} />
        </form>
      </div>

      {/* Currency */}
      <div className="currency">
        <button onClick={() => setCurrencyTag('usd')}>USD</button>
        <button onClick={() => setCurrencyTag('inr')}>INR</button>
      </div>

      {/* table head */}
      <table>
        <tr>
          <th style={{width: "31%", textAlign: "center"}} className="first">Coin</th>
          <th style={{width: "13%"}}>Price</th>
          <th style={{width: "10%"}}>24h</th>
          <th style={{width: "22%"}}>24h Volume</th>
          <th>Mkt Cap</th>
        </tr>
      </table>

      {/* Coin data */}
      {filteredCoins?.map(coin => {
        return (
          <Coin key={coin.id} 
          name={coin.name} 
          image={coin.image}
          symbol={coin.symbol}
          volume={coin.total_volume}
          price={coin.current_price}
          priceChange={coin.price_change_percentage_24h_in_currency}
          marketcap = {coin.market_cap}
          currencyTag={currencyTag==='usd'? '$': '₹'}
          data={coin.sparkline_in_7d.price}
          />
        )
      })}
      
    </div>
  );
}

export default App;
