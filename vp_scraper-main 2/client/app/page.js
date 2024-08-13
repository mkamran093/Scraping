"use client"

import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import productService from "./service"
import { SchedulerForm } from "./form";
import { Button } from "@/components/ui/button";
import React, { useEffect, useState } from "react";

export default function Home() {
  
  const [totalProducts, setTotalProducts] = useState(0);
  const [failedProducts, setFailedProducts] = useState(0);

  const updateProductCounts = async () => {
    try {
    const totalCountResponse = await productService.getProductCount();
    const failedCountResponse = await productService.getFailedProductCount();
    
    const totalCount = totalCountResponse.total_products;
    const failedCount = failedCountResponse.failed_products;

      setTotalProducts(totalCount);
      setFailedProducts(failedCount);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    updateProductCounts();
  }, []);

  return (
    <main className=''>
      <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
        <StatusCard title='Total Products' content={totalProducts} />
        <StatusCard title='Total Failed Products' content={failedProducts} />
        <Card className='md:col-span-1'>
          <CardHeader>
            <CardTitle>Product Management</CardTitle>
            <CardDescription>
              Perform various actions on your products.
            </CardDescription>
          </CardHeader>
          <CardContent className='grid gap-2'>
            <Button variant='outline' onClick={async () => {
  await productService.loadToWooCommerce();
  updateProductCounts();
}} >Load to WooCommerce</Button>
            <Button variant='outline' onClick={async () => {
  await productService.triggerFullScraping();
  updateProductCounts();
}}>Scrape Product</Button>
            <Button variant='outline' onClick={async () => {
  await productService.triggerPriceScraping();
  updateProductCounts();
}}>Scrape Price</Button>
          </CardContent>
        </Card>
        <Card className='md:col-span-2'>
          <CardHeader>
            <CardTitle>Scheduler Form</CardTitle>
          </CardHeader>
          <CardContent>
            <SchedulerForm />
          </CardContent>
        </Card>
      </div>
      <div className='py-14'>
        <ProductsTable />
      </div>
    </main>
  );
}

function StatusCard(props) {
  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>{props.title}</CardTitle>
        </CardHeader>
        <CardContent>{props.content}</CardContent>
      </Card>
    </>
  );
}

function ProductsTable() {
  return (
    <>
      <Table>
        <TableCaption>A list of scraped Products</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Name</TableHead>
            <TableHead>Description</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell></TableCell>
            <TableCell></TableCell>
            <TableCell></TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </>
  );
}
