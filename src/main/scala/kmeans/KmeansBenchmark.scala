package kmeans

import scala.collection._
import scala.util.Random
import scala.Predef.augmentString
import scala.Predef.intWrapper
import scala.{Int, Double, Boolean}
import java.lang.String

class Point(val x: Double, val y: Double, val z: Double) {
  private def square(v: Double): Double = v * v
  def squareDistance(that: Point): Double = {
    square(that.x - x) + square(that.y - y) + square(that.z - z)
  }
  private def round(v: Double): Double = (v * 100).toInt / 100.0
  override def toString =
    "(" + round(x) + "}, " + round(y) + ", " + round(z) + ")"
}

object KmeansBenchmark extends communitybench.Benchmark {
  def generatePoints(k: Int, num: Int): Seq[Point] = {
    val randx = new Random(1)
    val randy = new Random(3)
    val randz = new Random(5)
    (0 until num)
      .map({ i =>
        val x = ((i + 1) % k) * 1.0 / k + randx.nextDouble() * 0.5
        val y = ((i + 5) % k) * 1.0 / k + randy.nextDouble() * 0.5
        val z = ((i + 7) % k) * 1.0 / k + randz.nextDouble() * 0.5
        new Point(x, y, z)
      })
      .to[mutable.ArrayBuffer]
  }

  def initializeMeans(k: Int, points: Seq[Point]): Seq[Point] = {
    val rand = new Random(7)
    (0 until k)
      .map(_ => points(rand.nextInt(points.length)))
      .to[mutable.ArrayBuffer]
  }

  def findClosest(p: Point, means: GenSeq[Point]): Point = {
    scala.Predef.assert(means.size > 0)
    var minDistance = p.squareDistance(means(0))
    var closest     = means(0)
    for (mean <- means) {
      val distance = p.squareDistance(mean)
      if (distance < minDistance) {
        minDistance = distance
        closest = mean
      }
    }
    closest
  }

  def classify(
      points: GenSeq[Point],
      means: GenSeq[Point]
  ): GenMap[Point, GenSeq[Point]] = {
    val grouped = points.groupBy(p => findClosest(p, means))
    means.foldLeft(grouped) { (map, mean) =>
      if (map.contains(mean)) map else map.updated(mean, Seq())
    }
  }

  def findAverage(oldMean: Point, points: GenSeq[Point]): Point =
    if (points.length == 0) oldMean
    else {
      var x = 0.0
      var y = 0.0
      var z = 0.0
      points.seq.foreach { p =>
        x += p.x
        y += p.y
        z += p.z
      }
      new Point(x / points.length, y / points.length, z / points.length)
    }

  def update(
      classified: GenMap[Point, GenSeq[Point]],
      oldMeans: GenSeq[Point]
  ): GenSeq[Point] = {
    oldMeans.map(mean => findAverage(mean, classified(mean)))
  }

  def converged(eta: Double)(
      oldMeans: GenSeq[Point],
      newMeans: GenSeq[Point]
  ): Boolean = {
    (oldMeans zip newMeans)
      .map({
        case (oldMean, newMean) =>
          oldMean squareDistance newMean
      })
      .forall(_ <= eta)
  }

  final def kMeans(
      points: GenSeq[Point],
      means: GenSeq[Point],
      eta: Double
  ): GenSeq[Point] = {
    val classifiedPoints = classify(points, means)

    val newMeans = update(classifiedPoints, means)

    if (!converged(eta)(means, newMeans)) {
      kMeans(points, newMeans, eta)
    } else {
      newMeans
    }
  }

  def run(input: String): Boolean = {
    val numPoints              = input.toInt
    val eta                    = 0.01
    val k                      = 32
    val points                 = generatePoints(k, numPoints)
    val means                  = initializeMeans(k, points)
    var centers: GenSeq[Point] = null
    val result                 = kMeans(points, means, eta)
    var sum                    = 0D
    result.foreach { p =>
      sum += p.x
      sum += p.y
      sum += p.z
    }
    sum == 71.5437923802926D
  }

  override def main(args: Array[String]): Unit =
    super.main(args)
}
