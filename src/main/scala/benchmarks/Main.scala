package benchmarks

import java.lang.System.exit

object Main {
  val benchmarks = Discover.discovered.sortBy(_.getClass.getSimpleName)
  def main(args: Array[String]): Unit = {
    assert(args.size == 2, "need to provide iterations and output file")
    val iterations = args(0).toInt
    val outpath    = args(1)
    assert(benchmarks.size == 1, "one benchmark at a time")
    val benchmark                                = benchmarks.head
    val BenchmarkCompleted(_, _, times, success) = benchmark.loop(iterations)
    assert(success, "validation failed")
    val out = new java.io.PrintWriter(outpath)
    var i   = 0
    while (i < times.length) {
      out.write(times(i).toString)
      out.write("\n")
      i += 1
    }
    out.close()
  }
}
