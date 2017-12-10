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

import benchmarks._
import som._

class CDBenchmark extends benchmarks.Benchmark[Int] {
  override val runningTime: BenchmarkRunningTime =
    LongRunningTime

  override def run(): Int =
    benchmark(100)

  override def check(res: Int): Boolean =
    res == 4305

  def benchmark(numAircrafts: Int): Int = {
    val numFrames        = 200
    val simulator        = new Simulator(numAircrafts);
    val detector         = new CollisionDetector();
    var actualCollisions = 0

    (0 until numFrames).map { i =>
      val time       = i / 10.0
      val collisions = detector.handleNewFrame(simulator.simulate(time))
      actualCollisions += collisions.size()
    }

    actualCollisions
  }
}
