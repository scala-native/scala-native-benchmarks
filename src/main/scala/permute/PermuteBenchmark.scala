package permute

import scala.Predef.intWrapper
import scala.Predef.augmentString
import scala.{Int, Boolean, Unit}
import java.lang.String

object PermuteBenchmark extends communitybench.Benchmark {
  def run(input: String): Int = {
    val size     = input.toInt
    val permIter = (0 until size).toList.permutations

    var count = 0
    while (permIter.hasNext) {
      permIter.next()
      count += 1
    }
    count
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

  override def main(args: Array[String]): Unit =
    super.main(args)
}
