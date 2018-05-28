/* The Computer Language Benchmarks Game
 * http://shootout.alioth.debian.org/
 *
 * Based on nbody.java and adapted basde on the SOM version.
 */
package nbody

import scala.{Double, Boolean}
import java.lang.String
import scala.Predef.augmentString

object NbodyBenchmark extends communitybench.Benchmark {
  def run(input: String): Boolean = {
    val system = new NBodySystem()
    val n      = input.toInt

    var i = 0
    while (i < n) {
      system.advance(0.01)
      i += 1
    }

    system.energy() == -0.1690859889909308
  }

  override def main(args: Array[String]): Unit =
    super.main(args)
}
