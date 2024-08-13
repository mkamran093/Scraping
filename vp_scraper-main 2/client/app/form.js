"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import productService from "@/app/service";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { toast } from "@/components/ui/use-toast";

const SchedulerSchema = z.object({
  scrape_all_interval_hours: z
    .number()
    .transform((val) => Number(val))
    .refine(val => !isNaN(val) && val >= 1, "Must be at least 1 hour")
    .optional(),
  scrape_price_interval_hours: z
    .number()
    .transform((val) => Number(val))
    .refine(val => !isNaN(val) && val >= 1, "Must be at least 1 hour")
    .optional(),
});

export function SchedulerForm() {
  const form = useForm({
    resolver: zodResolver(SchedulerSchema),
    defaultValues: {
      scrape_all_interval_hours: undefined,
      scrape_price_interval_hours: undefined,
    },
  });

  const onSubmit = async (data) => {
    // Convert hours to seconds for the API request
    const requestData = {
      scrape_all_interval_seconds:
        data.scrape_all_interval_hours !== undefined
          ? Number(data.scrape_all_interval_hours) * 3600
          : undefined,
      scrape_price_interval_seconds:
        data.scrape_price_interval_hours !== undefined
          ? Number(data.scrape_price_interval_hours) * 3600
          : undefined,
    };

    try {
      const response = await productService.configureScheduler(requestData);
      toast({
        title: "Scheduler updated",
        description: response.message,
      });
    } catch (error) {
      toast({
        title: "Error updating scheduler",
        description:
          "An error occurred while attempting to update the scheduler.",
      });
      console.error(error);
    }
  };

  // Check if both fields are empty
  const isSubmitDisabled =
    form.watch("scrape_all_interval_hours") &&
    form.watch("scrape_price_interval_hours");

  return (
    <Form {...form}>
      <form
        onSubmit={form.handleSubmit(onSubmit)}
        className='flex flex-col space-y-4'
      >
        <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
          <FormField
            control={form.control}
            name='scrape_all_interval_hours'
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Scrape All Interval (hours)</FormLabel>
                <FormControl>
                  <Input type='number' {...field} />
                </FormControl>
                {fieldState.error && (
                  <FormMessage>{fieldState.error.message}</FormMessage>
                )}
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='scrape_price_interval_hours'
            render={({ field, fieldState }) => (
              <FormItem>
                <FormLabel>Scrape Price Interval (hours)</FormLabel>
                <FormControl>
                  <Input type='number' {...field} />
                </FormControl>
                {fieldState.error && (
                  <FormMessage>{fieldState.error.message}</FormMessage>
                )}
              </FormItem>
            )}
          />
        </div>

        <Button type='submit' disabled={!isSubmitDisabled}>
          Update Scheduler
        </Button>
      </form>
    </Form>
  );
}
