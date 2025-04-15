import axios from "axios";
import { Product } from "./types";

export const searchProducts = async (query: string, requestBody: any) => {
  const response = await axios.post(
    `http://localhost:8000/products/search?q=${encodeURIComponent(query)}`,
    requestBody,
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
  return response.data; // Assuming the response data contains the product results
};
