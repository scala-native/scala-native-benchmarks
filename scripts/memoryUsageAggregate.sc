//> using lib "com.lihaoyi::os-lib:0.9.0"
import os.*

val configs = Seq(
  // "scala-native-0.4.0-2.11",
)

case class Result(config: String, benchmark: String, memoryUsage: Seq[Int]) {
  def averageMemoryUsage = memoryUsage.sum / memoryUsage.size
}

val results: Seq[Result] = for {
  config    <- configs
  benchmark <- os.list(pwd / "results" / config)
  memUsageFile = benchmark / "memory_usage" if exists(memUsageFile)
  memoryUsage  = read.lines(memUsageFile).map(java.lang.Integer.parseInt).toList
} yield Result(config, benchmark.last, memoryUsage)

val grouped = results
  .sortBy(_.averageMemoryUsage)
  .groupBy(_.benchmark)

println((("benchmark") +: configs).mkString(","))
grouped.foreach { case (bench, results) =>
  val values = configs.toList
    .map { c =>
      results
        .find(_.config == c)
        .map(_.averageMemoryUsage)
        .getOrElse(-1)
    }
    .mkString(",")
  println(s"$bench,$values")
}
