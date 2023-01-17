package communitybench

import java.lang.{String, System}

abstract class Benchmark {
  def run(input: String): Any

  def main(args: Array[String]): Unit = {
    assert(
      args.length == 4,
      "4 arguments expected: number of batches, batch size, input and expected output")
    val batches   = args(0).toInt
    val batchSize = args(1).toInt
    val input     = args(2)
    val output    = args(3)

    loop(batches, batchSize, input, output)
      .foreach(println)
  }

  def loop(batches: Int,
           batchSize: Int,
           input: String,
           output: String): Array[Long] = {
    assert(batches >= 1)
    assert(batchSize >= 1)

    Array.fill(batches){
      val start = System.nanoTime()
      val results = Array.fill(batchSize)(run(input))
      val end = System.nanoTime()
      
      results.find(_.toString != output)
      .foreach{result => 
        throw new Exception(
          "validation failed: expected `" + output + "` got `" + result + "`")
      }
      end - start
    }
  }
}
