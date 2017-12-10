package permute

import benchmarks.{BenchmarkRunningTime, LongRunningTime}

class PermuteBenchmark extends benchmarks.Benchmark[Int] {
  val size = 6

  override val runningTime: BenchmarkRunningTime =
    LongRunningTime

  override def run(): Int = {
    val permIter = (0 until size).toList.permutations

    var count = 0
    while (permIter.hasNext) {
      permIter.next()
      count += 1
    }
    count
  }

  override def check(value: Int): Boolean = {
    value == factorial(size)
  }

  private def factorial(i: Int): Int = {
    var n    = i
    var fact = 1
    while (n > 0) {
      fact *= n
      n -= 1
    }
    fact
  }
}
