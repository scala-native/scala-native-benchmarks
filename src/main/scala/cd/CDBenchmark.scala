/*
 * Copyright (c) 2001-2016 Stefan Marr
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the 'Software'), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
package cd

import som._
import scala.Predef.augmentString
import scala.Predef.intWrapper
import scala.{Int, Boolean}
import java.lang.String

object CDBenchmark extends communitybench.Benchmark {
  def run(input: String): Int = {
    val numAircrafts     = input.toInt
    val numFrames        = 200
    val simulator        = new Simulator(numAircrafts)
    val detector         = new CollisionDetector()
    var actualCollisions = 0

    (0 until numFrames).map { i =>
      val time       = i / 10.0
      val collisions = detector.handleNewFrame(simulator.simulate(time))
      actualCollisions += collisions.size()
    }

    actualCollisions
  }

  override def main(args: Array[String]): Unit =
    super.main(args)
}
