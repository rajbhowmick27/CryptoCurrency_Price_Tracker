import React from "react";
import "./Coin.css";

const Coin = ({
  name,
  image,
  symbol,
  price,
  volume,
  priceChange,
  marketcap,
  currencyTag,
  data
}) => {
  return (
    <div className="coin-container">
      <div className="coin-row">
        <div className="coin">
          <img src={image} alt="crypto" />
          <h1>{name}</h1>
          <p className="coin-symbol">{symbol}</p>
          <p className="coin-price">
            {currencyTag}
            {price}
          </p>
          {priceChange < 0 ? (
            <p className="coin-percent red">{priceChange.toFixed(2)}</p>
          ) : (
            <p className="coin-percent green">{priceChange.toFixed(2)}</p>
          )}
          <p className="coin-volume">
            {currencyTag}
            {volume.toLocaleString()}
          </p>
          <p className="coin-marketcap">
            {currencyTag}
            {marketcap.toLocaleString()}
          </p>

         
        </div>
      </div>
    </div>
  );
};

export default Coin;
