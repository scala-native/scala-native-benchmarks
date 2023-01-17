package histogram

import scala.util.Random

object Histogram extends communitybench.Benchmark{
  override def run(input: String): Any = {
    val Array(items, k) = input.split(",").map(_.toInt)
    var histogram = Map.empty[Int, Int]
    val random = new Random(13371337)
    (1 to items).foreach {
      _ =>
        val key = random.nextInt(k)
        val newValue = histogram.getOrElse(key, 0) + 1
        histogram += key -> newValue
    }
    histogram.values.sum == items
  }

  override def main(args: Array[String]): Unit =
    super.main(args)
}
