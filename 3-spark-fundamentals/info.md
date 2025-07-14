# Notes
In this folder there are hand-written notes from the three lectures on Spark.

Notebooks in the `/notebooks/` folder are copied over from [data-engineer-handbook](https://github.com/DataExpert-io/data-engineer-handbook/blob/main/bootcamp/materials/3-spark-fundamentals/) with my own edits and notes added in.

# Homework
PySpark notebook for part 1 of the homework is at `./homework/src/notebooks/`.

CSV files containing data for the homework are at `./data/`.

To run the jobs or tests you'll need an environment built from the Dockerfile in the root of this project. I've been using it to build a VSCode dev container that has Java, Python and Spark dependencies.

Once you have that, you can run the tests with
```
python -m pytest
```