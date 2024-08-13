import axios from "axios";

// Configure the base URL for your FastAPI service
const api = axios.create({
  baseURL: "http://localhost:8000", // Adjust according to your FastAPI base URL
  headers: {
    "Content-Type": "application/json",
  },
});

const productService = {
  // Get all products
  getAllProducts: async () => {
    try {
      const response = await api.get("/products/");
      return response.data;
    } catch (error) {
      console.error("Error fetching all products:", error);
      throw error;
    }
  },

  // Get the total number of products
  getProductCount: async () => {
    try {
      const response = await api.get("/product-count/");
      return response.data;
    } catch (error) {
      console.error("Error fetching product count:", error);
      throw error;
    }
  },

  // Get the number of products with `failed: true`
  getFailedProductCount: async () => {
    try {
      const response = await api.get("/failed-product-count/");
      return response.data;
    } catch (error) {
      console.error("Error fetching failed product count:", error);
      throw error;
    }
  },

  // Trigger full scraping
  triggerFullScraping: async () => {
    try {
      const response = await api.post("/trigger_scraping/");
      return response.data;
    } catch (error) {
      console.error("Error triggering full scraping:", error);
      throw error;
    }
  },

  // Trigger price scraping
  triggerPriceScraping: async () => {
    try {
      const response = await api.post("/trigger_price_scraping/");
      return response.data;
    } catch (error) {
      console.error("Error triggering price scraping:", error);
      throw error;
    }
  },

  // Configure the scheduler intervals
  configureScheduler: async (scheduleConfig) => {
    try {
      const response = await api.post("/configure-scheduler/", scheduleConfig);
      return response.data;
    } catch (error) {
      console.error("Error configuring scheduler:", error);
      throw error;
    }
  },

  // Load Data to WooCommerce
  loadToWooCommerce: async () => {
    try {
      const response = await api.get("/load-to-woocommerce/");
      return response.data;
    } catch (error) {
      console.error("Error loading data to WooCommerce:", error);
      throw error;
    }
  },
};

export default productService;
