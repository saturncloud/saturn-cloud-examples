library(tidyverse)
library(fs)
library(jsonlite)
library(glue)

data <- 
  dir_ls("training-comparisons/2021-02-18T20_05_31.301849", recurse=TRUE, regexp = ".json$") %>%
  str_match("^training-comparisons/2021-02-18T20_05_31.301849/batch=([0-9]+)\\&num_workers=([0-9]+)\\&learning_rate_multiplier=([0-9\\.]+)/logs/data_([0-9])+_.*") %>%
  as_tibble(.name_repair = ~ c("path", "batch", "num_workers", "learning_rate_multiplier", "worker")) %>%
  mutate_at(vars(batch, num_workers, worker,learning_rate_multiplier), as.numeric) %>%
  mutate(data = map(path, read_json)) %>%
  select(-path, -worker) %>%
  unnest_wider(data) %>%
  ungroup()


data %>%
  filter(worker == 0) %>%
  mutate(group = glue("workers={num_workers} batch={batch} learning-multi={learning_rate_multiplier}")) %>%
  ggplot(aes(x=elapsed_time, y = loss, group = group, color = group, shape = factor(num_workers))) +
    geom_point() +
    geom_line()

data %>%
  filter(worker == 0) %>%
  mutate(group = glue("workers={num_workers} batch={batch} learning-multi={learning_rate_multiplier}")) %>%
  ggplot(aes(x=epoch, y = loss, group = group, color = group, shape = factor(num_workers))) +
  geom_point() +
  geom_line()