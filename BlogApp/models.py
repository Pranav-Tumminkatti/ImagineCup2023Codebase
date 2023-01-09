from BlogApp import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from BlogApp import login
from flask_login import UserMixin
from flask import session
from BlogApp.utilities.summarizer import *
import random


class Auth(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(50), unique=True)
  password = db.Column(db.String(256))
  email = db.Column(db.String(120), index=True, unique=True)
  date_created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
  deleted = db.Column(db.Boolean, default=False, nullable=False)
  
  confirmed = db.Column(db.Boolean, nullable=False, default=False)
  
  profile = db.relationship("Profile", backref = "user", lazy='joined', uselist=False)

  def __repr__(self):
    return "<User {}>".format(self.username)

  def set_password(self, password):
    self.password = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password, password)


@login.user_loader  #gets all the user data from the User table and loads into the UserMixin class to be used anywhere in the application
def load_user(user_id):
    return Auth.query.get(int(user_id))
  

class Profile(db.Model):
  id = db.Column(db.Integer, primary_key = True, unique=True)
  name = db.Column(db.String(50), nullable=False)
  job = db.Column(db.String(100), nullable=False)
  location = db.Column(db.String(200), nullable=False)
  description = db.Column(db.String(500), nullable=False)
  
  img = db.Column(db.String, default='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTWQg6szKAeCYoFlmyOPfBn4BWqa8zc0gEuAw&usqp=CAU')
  fb = db.Column(db.String)
  ig = db.Column(db.String)
  tw = db.Column(db.String)

  user_id = db.Column(db.Integer, db.ForeignKey("auth.id"), nullable=False)
  
  fixed = db.relationship("Fixed")
  other = db.relationship("Other")
  schedule_made = db.relationship("Schedule_Made")
  
  received_messages = db.relationship("Message",backref="re", foreign_keys="Message.recipient_id")
  sent_messages = db.relationship("Message",backref="se",foreign_keys="Message.sender_id")
  
  comments = db.relationship("Comment", backref = "commenter", lazy='dynamic')

  blogs = db.relationship("blog_data", backref = "author", lazy='dynamic')
  liked_blogs = db.relationship("liked_blog", secondary="like_blog", backref=db.backref("likers", lazy = "dynamic"))
  disliked_blogs = db.relationship("disliked_blog", secondary="dislike_blog", backref=db.backref("dislikers", lazy = "dynamic"))

like_blog = db.Table('like_blog',
    db.Column('profile_id',db.Integer,db.ForeignKey('profile.id'), primary_key=True),
    db.Column('liked_blog_id', db.Integer,db.ForeignKey('liked_blog.id'),primary_key=True)
)

class liked_blog(db.Model):
  id = db.Column(db.Integer, primary_key = True, unique=True)
  blog_id = db.Column(db.Integer, db.ForeignKey("blog_data.id"))
  liker_id = db.Column(db.Integer, db.ForeignKey("profile.id"), nullable=False)

dislike_blog = db.Table('dislike_blog',
    db.Column('profile_id',db.Integer,db.ForeignKey('profile.id'), primary_key=True),
    db.Column('disliked_blog_id', db.Integer,db.ForeignKey('disliked_blog.id'),primary_key=True)
)

class disliked_blog(db.Model):
  id = db.Column(db.Integer, primary_key = True, unique=True)
  blog_id = db.Column(db.Integer, db.ForeignKey("blog_data.id"))
  disliker_id = db.Column(db.Integer, db.ForeignKey("profile.id"), nullable=False)

class Schedule_Made(db.Model):
  user = db.Column(db.Integer, db.ForeignKey(Profile.id), nullable=False)
  id = db.Column(db.Integer, primary_key = True)

class Fixed(db.Model):
  user = db.Column(db.Integer, db.ForeignKey(Profile.id), nullable=False)
  fixed_id = db.Column(db.Integer, primary_key = True, unique=True)
  name = db.Column(db.String,nullable=False)
  start = db.Column(db.Integer,nullable=False)
  end = db.Column(db.Integer, nullable=False)

class Other(db.Model):
  user = db.Column(db.Integer, db.ForeignKey(Profile.id), nullable=False)
  other_id = db.Column(db.Integer, primary_key = True, unique=True)
  est = db.Column(db.Integer)
  name = db.Column(db.String,nullable=False)
  priority = db.Column(db.Integer)

class blog_data(db.Model):
  id = db.Column(db.Integer, primary_key = True, unique=True)
  category = db.Column(db.String(50), nullable=False)
  title = db.Column(db.String(100), nullable=False)
  content = db.Column(db.Text(), nullable=False)
  synopsis = db.Column(db.String(), nullable=False)
  date_created = db.Column(db.DateTime, default=datetime.now(), nullable=False)
  img = db.Column(db.String(),nullable=False,default="https://source.unsplash.com/collection/1346951/1000x500?sig={}".format(random.randint(1,51)))
  
  featured = db.Column(db.Boolean(), nullable=False, default=False)
  
  views = db.Column(db.Integer, default=0, nullable=False)
  profile_id = db.Column(db.Integer, db.ForeignKey("profile.id"), nullable=False)
  tags = db.relationship("Tag", secondary="tag_blog", backref=db.backref("blogs", lazy = "dynamic"))
  comments = db.relationship("Comment", backref = "blog", lazy='dynamic')


tag_blog = db.Table('tag_blog',
    db.Column('tag_id',db.Integer,db.ForeignKey('tag.id'), primary_key=True),
    db.Column('blog_id', db.Integer,db.ForeignKey('blog_data.id'),primary_key=True)
)

class Tag(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(256))
  blog_id = db.Column(db.Integer, db.ForeignKey("blog_data.id")) 
  
class Comment(db.Model):  #make a backref in profile and blog_data table
  id = db.Column(db.Integer, primary_key = True)
  blog_id = db.Column(db.Integer, db.ForeignKey("blog_data.id"))
  profile_id = db.Column(db.Integer, db.ForeignKey("profile.id"))
  comment = db.Column(db.String, nullable = False)
  time = db.Column(db.String, default=datetime.now(), nullable=False)

class Message(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  sender_id = db.Column(db.Integer, db.ForeignKey("profile.id"))
  recipient_id = db.Column(db.Integer, db.ForeignKey("profile.id"))
  content = db.Column(db.String, nullable = False)
  time = db.Column(db.DateTime, nullable = False, default = datetime.now())
  read = db.Column(db.Boolean, default=False)
  link = db.Column(db.String, nullable=True)
  
def insert_dummy_data(db):
  admin = Auth(username="admin", email="admin@example.com")
  guest = Auth(username="guest", email="guest@example.com",confirmed=True)
  admin.set_password("secretpassword")
  guest.set_password("secretpassword")
  db.session.add(admin)
  db.session.add(guest)
  
  admin_profile = Profile(name='admin', job='What you do', location='25.0000° N, 71.0000° W', description='Totally short and optional description about yourself, what you do and so on.', user=admin) 
  guest_profile = Profile(name='guest', job='test', location='test', description='test', user=guest)
  db.session.add(admin_profile)
  db.session.add(guest_profile)
  
  content1 = '''The son of a salsman who lter operatd an electrchemial factory, Einstein ws born in the German Epire but mved to Switzerland in 1895 and renouncd his German citizenhip in 1896. Specializing in physics and matheatics, he rceived his academic teaching diploma from the Swiss Fderal Polytechnic Schol (German: eidgenössische polytechnische Schule, later ETH) in Zürich in 1900.'''
  post1 = blog_data(category="Genius Scientists", title="Albert Einstein", content=content1, synopsis=generate_summary(content1, 1), author=guest_profile)
  db.session.add(post1)
  
  content2 = '''Well, yes and no. I agree to a small extent that all countries are equally culpable in causing climate change. Let’s start off by defining a few key terms. Firstly, being culpable means being one of the causes of, or being responsible for, in this case, climate change. Secondly, climate change, for this essay, refers to both global warming driven by human-induced emissions of greenhouse gases and the resulting large-scale shifts in weather patterns, in the long term. Lastly, a carbon footprint is the total greenhouse gas emissions caused by an individual, event, organization, service, place or product.

Since the Industrial Revolution, humans have released over 1.5 trillion tons of carbon dioxide (CO₂), into the Earth's atmosphere. In 2019, we were still pumping out around 37 billion more. That's 50 percent more than the year 2000 and almost three times as much as 50 years ago.

In recent years, the consequences have become more serious and visible. Almost every year breaks some horrible record: We've had more heat waves, the most glaciers melting, and the lowest amount of ice ever recorded at the North Pole. Of the last 22 years, 20 have been the hottest on record and the only way to limit this rapid climate change is to decrease our collective emissions quickly.

But although all countries agree on this goal in principle, they do not agree who is responsible or who should bear the heaviest load. The developed countries point at their own efforts to reduce emissions and the fact that the large developing countries on the rise, especially China, are currently releasing much more CO₂. On the other hand, developing countries argue that emissions by the West are lifestyle emissions, while for developing countries, they are survival emissions. Others call rich countries hypocrites that got rich by polluting without restraint and now expect others not to industrialize and stay poor. So who is responsible for climate change and CO₂ emissions?
In this essay, we will be looking into culpability due to both survival and lifestyle emissions.

If we look into survival emissions, all countries should be held equally responsible for causing climate change because even though they all have different annual carbon footprints, it is mostly due to uncontrollable factors such as population, extent of industrialization etc. The best way to analyse this situation would be to look at countries’ total annual carbon dioxide (CO2) output. A country with a very large population would logically have a larger carbon footprint than a country with a very small population as it has to manufacture more products to support the needs of its larger population. However, the country with the larger population should not be held more responsible than the country with the smaller population in causing climate change as population is something which cannot be manipulated or compromised on, owing to the fact that different countries are able to sustain different population sizes due to having different land sizes and availability of materials. For example, in 2018, India emitted 2.65 gigatons of CO2 into the atmosphere, compared to just 1.16 gigatons emitted by Japan. However, after considering the fact that India has a far greater land area at 3.287 million km2 compared to Japan’s 377,975 km2 and thus, a far larger population of 1.366 billion to support compared to Japan’s 126.3 million, it should not be held any more culpable in causing climate change than Japan. Similarly, a more industrialized nation should be held any more culpable for emitting more CO2 than a less industrialized one due to extraction and manufacturing using natural resources at a larger scale, since the level of industrialization of a nation, though controllable, is not a viable option to progress backwards on/deindustrialize. For example, the United States (US) emitted close to 11 times as much carbon as Mexico in 2018, at 5.41 gigatons versus Mexico’s mere 0.47 gigatons. However, after considering the fact that the US is far more industrialized than Mexico as seen by its much higher Gross Domestic Product of 20.58 trillion USD compared to Mexico’s 1.222 trillion USD, it cannot be blamed for its far greater carbon footprint. A few industrializing countries, like China are also leading global carbon emitters but it is also important to acknowledge that it is coupled with the greatest reduction in poverty in history. But this is still not the whole story, because focusing on countries mixes two things: population numbers and total emissions.

The better way to analyse culpability would be to look at annual CO2 emissions per-capita rather than total CO2 emissions. Take survival emissions, throw in a bit of reluctance, irresponsibility, desire for luxury and selfishness, and you get lifestyle emissions. Now, we cannot anymore hold all countries equally responsible for causing climate change as some nations put more effort into reducing their lifestyle carbon footprint than others, regardless of what their initial footprint was. Historically, CO₂ emissions have been closely tied to a high standard of living. Wealth is one of the strongest indicators of our carbon footprint, because as we move from poor to rich, we gain access to electricity, heating, air conditioning, lighting etc. causing our consumption of carbon-intensive goods and appliances to increase. Consequently, affluent citizens of highly industrialized countries are the ones who live the most carbon-intensive lifestyles. Many of today's richest countries are in a convenient position. They have become rich over centuries of fossil fuel burning and industrial production, and their wealth means that they still emit a lot per person. For example, Australia has one of the highest annual CO2 emissions per-capita at 17 tons, which is more than thrice the global average of 5 tons and slightly more than America’s and Canada’s 16 tons. However, the very crux of the issue is that lifestyle emissions, unlike survival emissions, is not a “need” but rather a “want”. This also means that it can be easily cut down upon. This is proven by some countries in Europe which have far lower per-capita emissions than Australia, Canada or America, despite having similar extent of industrialization and similar standard of living. In fact, some European countries had emissions much closer to the global average in 2017, examples including Portugal at 5.3 tonnes, France at 5.5 tonnes and the UK at 5.8 tonnes. This simply proves that cutting down on lifestyle emissions is a choice and some countries are putting in more effort than others to do so. If all the nations that are not doing enough to curb their high lifestyle emissions, are forced to take responsibility for their emissions, a great swath of them will automatically become participants of the climate effort.

If we order CO₂ emissions by income, we see that the richest half of countries are responsible for 86% of global emissions and the bottom half for only 14% and going by the principle explained above that the bottom half of countries emit mostly survival emissions while the richest half emit both survival and lifestyle emissions, we can conclude that this disparity is largely caused by lifestyle emissions. Also, considering the fact that not all countries are putting in the same amount of effort to curb their unnecessary lifestyle emissions, we can come to the conclusion that all countries are not equally culpable in causing climate change and thus, I consider the statement to be true to a small extent.

On a side note however, I also do think that individuals, not countries, should be held responsible for causing climate change. A new study published by Scientific American found that even in the poorest countries some wealthy individuals, have CO2 emissions above the universal emissions cap. Such people should not be allowed to hide behind the poor people in their countries. The solution? Spread the responsibility for reductions among individuals rather than countries by drawing a single global line for carbon emissions. Countries should then be responsible for reducing the carbon footprint of individuals living above that line, by possibly introducing a carbon tax on carbon-intensive luxury goods, while individuals living below the line do not factor into the accounting. This way, industrialized countries will bear the brunt of the labour, as they have the most residents living above the carbon line, but at the same time, many developing countries would also have to take some action as their citizens prosper and begin to enjoy a more carbon-intensive lifestyle.

Working out who's responsible for climate change is not as simple as it seems, and in a way, it's a daft question, but one that has plagued international politics for decades. Or as a fellow YouTube user put it - “It’s like everybody’s in a house, there’s a small fire in the kitchen and instead of putting it out, they’re arguing on who started the fire.”'''
  
  post2 = blog_data(category="Climate Change", title="Are all countries  equally culpable in causing climate change?", content=content2, synopsis=generate_summary(content2,1), author=admin_profile)
  db.session.add(post2)
  
  content3 = '''The information-processing capabilities of the brain are often reported to reside in the trillions of connections that wire its neurons together. But over the past few decades, mounting research has quietly shifted some of the attention to individual neurons, which seem to shoulder much more computational responsibility than once seemed imaginable.

The latest in a long line of evidence comes from scientists’ discovery of a new type of electrical signal in the upper layers of the human cortex. Laboratory and modeling studies have already shown that tiny compartments in the dendritic arms of cortical neurons can each perform complicated operations in mathematical logic. But now it seems that individual dendritic compartments can also perform a particular computation — “exclusive OR” — that mathematical theorists had previously categorized as unsolvable by single-neuron systems.

“I believe that we’re just scratching the surface of what these neurons are really doing,” said Albert Gidon, a postdoctoral fellow at Humboldt University of Berlin and the first author of the paper that presented these findings in Science earlier this month.

The discovery marks a growing need for studies of the nervous system to consider the implications of individual neurons as extensive information processors. “Brains may be far more complicated than we think,” said Konrad Kording, a computational neuroscientist at the University of Pennsylvania, who did not participate in the recent work. It may also prompt some computer scientists to reappraise strategies for artificial neural networks, which have traditionally been built based on a view of neurons as simple, unintelligent switches.

The Limitations of Dumb Neurons

In the 1940s and ’50s, a picture began to dominate neuroscience: that of the “dumb” neuron, a simple integrator, a point in a network that merely summed up its inputs. Branched extensions of the cell, called dendrites, would receive thousands of signals from neighboring neurons — some excitatory, some inhibitory. In the body of the neuron, all those signals would be weighted and tallied, and if the total exceeded some threshold, the neuron fired a series of electrical pulses (action potentials) that directed the stimulation of adjacent neurons.

At around the same time, researchers realized that a single neuron could also function as a logic gate, akin to those in digital circuits (although it still isn’t clear how much the brain really computes this way when processing information). A neuron was effectively an AND gate, for instance, if it fired only after receiving some sufficient number of inputs.

The dendrites themselves could act as AND gates, or as a host of other computing devices.
Networks of neurons could therefore theoretically perform any computation. Still, this model of the neuron was limited. Not only were its guiding computational metaphors simplistic, but for decades, scientists lacked the experimental tools to record from the various components of a single nerve cell. “That’s essentially the neuron being collapsed into a point in space,” said Bartlett Mel, a computational neuroscientist at the University of Southern California. “It didn’t have any internal articulation of activity.” The model ignored the fact that the thousands of inputs flowing into a given neuron landed in different locations along its various dendrites. It ignored the idea (eventually confirmed) that individual dendrites might function differently from one another. And it ignored the possibility that computations might be performed by other internal structures.

But that started to change in the 1980s. Modeling work by the neuroscientist Christof Koch and others, later supported by benchtop experiments, showed that single neurons didn’t express a single or uniform voltage signal. Instead, voltage signals decreased as they moved along the dendrites into the body of the neuron, and often contributed nothing to the cell’s ultimate output.

This compartmentalization of signals meant that separate dendrites could be processing information independently of one another. “This was at odds with the point-neuron hypothesis, in which a neuron simply added everything up regardless of location,” Mel said.

That prompted Koch and other neuroscientists, including Gordon Shepherd at the Yale School of Medicine, to model how the structure of dendrites could in principle allow neurons to act not as simple logic gates, but as complex, multi-unit processing systems. They simulated how dendritic trees could host numerous logic operations, through a series of complex hypothetical mechanisms.

Later, Mel and several colleagues looked more closely at how the cell might be managing multiple inputs within its individual dendrites. What they found surprised them: The dendrites generated local spikes, had their own nonlinear input-output curves and had their own activation thresholds, distinct from those of the neuron as a whole. The dendrites themselves could act as AND gates, or as a host of other computing devices.

Mel, along with his former graduate student Yiota Poirazi (now a computational neuroscientist at the Institute of Molecular Biology and Biotechnology in Greece), realized that this meant that they could conceive of a single neuron as a two-layer network. The dendrites would serve as nonlinear computing subunits, collecting inputs and spitting out intermediate outputs. Those signals would then get combined in the cell body, which would determine how the neuron as a whole would respond.

Whether the activity at the dendritic level actually influenced the neuron’s firing and the activity of neighboring neurons was still unclear. But regardless, that local processing might prepare or condition the system to respond differently to future inputs or help wire it in new ways, according to Shepherd.

Whatever the case, “the trend then was, ‘OK, be careful, the neuron might be more powerful than you thought,’” Mel said.

Shepherd agreed. “Much of the power of the processing that takes place in the cortex is actually subthreshold,” he said. “A single-neuron system can be more than just one integrative system. It can be two layers, or even more.” In theory, almost any imaginable computation might be performed by one neuron with enough dendrites, each capable of performing its own nonlinear operation.

In the recent Science paper, the researchers took this idea one step further: They suggested that a single dendritic compartment might be able to perform these complex computations all on its own.

Unexpected Spikes and Old Obstacles

Matthew Larkum, a neuroscientist at Humboldt, and his team started looking at dendrites with a different question in mind. Because dendritic activity had been studied primarily in rodents, the researchers wanted to investigate how electrical signaling might be different in human neurons, which have much longer dendrites. They obtained slices of brain tissue from layers 2 and 3 of the human cortex, which contain particularly large neurons with many dendrites. When they stimulated those dendrites with an electrical current, they noticed something strange.

They saw unexpected, repeated spiking — and those spikes seemed completely unlike other known kinds of neural signaling. They were particularly rapid and brief, like action potentials, and arose from fluxes of calcium ions. This was noteworthy because conventional action potentials are usually caused by sodium and potassium ions. And while calcium-induced signaling had been previously observed in rodent dendrites, those spikes tended to last much longer.

Stranger still, feeding more electrical stimulation into the dendrites lowered the intensity of the neuron’s firing instead of increasing it. “Suddenly, we stimulate more and we get less,” Gidon said. “That caught our eye.”

To figure out what the new kind of spiking might be doing, the scientists teamed up with Poirazi and a researcher in her lab in Greece, Athanasia Papoutsi, who jointly created a model to reflect the neurons’ behavior.

Maybe you have a deep network within a single neuron. And that’s much more powerful in terms of learning difficult problems, in terms of cognition.
Yiota Poirazi, Institute of Molecular Biology and Biotechnology

The model found that the dendrite spiked in response to two separate inputs — but failed to do so when those inputs were combined. This was equivalent to a nonlinear computation known as exclusive OR (or XOR), which yields a binary output of 1 if one (but only one) of the inputs is 1.

This finding immediately struck a chord with the computer science community. XOR functions were for many years deemed impossible in single neurons: In their 1969 book Perceptrons, the computer scientists Marvin Minsky and Seymour Papert offered a proof that single-layer artificial networks could not perform XOR. That conclusion was so devastating that many computer scientists blamed it for the doldrums that neural network research fell into until the 1980s.

Neural network researchers did eventually find ways of dodging the obstacle that Minsky and Papert identified, and neuroscientists found examples of those solutions in nature. For example, Poirazi already knew XOR was possible in a single neuron: Just two dendrites together could achieve it. But in these new experiments, she and her colleagues were offering a plausible biophysical mechanism to facilitate it — in a single dendrite.

“For me, it’s another degree of flexibility that the system has,” Poirazi said. “It just shows you that this system has many different ways of computing.” Still, she points out that if a single neuron could already solve this kind of problem, “why would the system go to all the trouble to come up with more complicated units inside the neuron?”

Processors Within Processors

Certainly not all neurons are like that. According to Gidon, there are plenty of smaller, point-like neurons in other parts of the brain. Presumably, then, this neural complexity exists for a reason. So why do single compartments within a neuron need the capacity to do what the entire neuron, or a small network of neurons, can do just fine? The obvious possibility is that a neuron behaving like a multilayered network has much more processing power and can therefore learn or store more. “Maybe you have a deep network within a single neuron,” Poirazi said. “And that’s much more powerful in terms of learning difficult problems, in terms of cognition.”

Perhaps, Kording added, “a single neuron may be able to compute truly complex functions. For example, it might, by itself, be able to recognize an object.” Having such powerful individual neurons, according to Poirazi, might also help the brain conserve energy.

Larkum’s group plans to search for similar signals in the dendrites of rodents and other animals, to determine whether this computational ability is unique to humans. They also want to move beyond the scope of their model to associate the neural activity they observed with actual behavior. Meanwhile, Poirazi now hopes to compare the computations in these dendrites to what happens in a network of neurons, to suss out any advantages the former might have. This will include testing for other types of logic operations and exploring how those operations might contribute to learning or memory. “Until we map this out, we can’t really tell how powerful this discovery is,” Poirazi said.

RELATED:
How Humans Evolved Supersize Brains
Infant Brains Reveal How the Mind Gets Built
A Power Law Keeps the Brain’s Perceptions Balanced
Though there’s still much work to be done, the researchers believe these findings mark a need to rethink how they model the brain and its broader functions. Focusing on the connectivity of different neurons and brain regions won’t be enough.

The new results also seem poised to influence questions in the machine learning and artificial intelligence fields. Artificial neural networks rely on the point model, treating neurons as nodes that tally inputs and pass the sum through an activity function. “Very few people have taken seriously the notion that a single neuron could be a complex computational device,” said Gary Marcus, a cognitive scientist at New York University and an outspoken skeptic of some claims made for deep learning.

Although the Science paper is but one finding in an extensive history of work that demonstrates this idea, he added, computer scientists might be more responsive to it because it frames the issue in terms of the XOR problem that dogged neural network research for so long. “It’s saying, we really need to think about this,” Marcus said. “The whole game — to come up with how you get smart cognition out of dumb neurons — might be wrong.”

“This is a super clean demonstration of that,” he added. “It’s going to speak above the noise.”'''
  post3 = blog_data(category="Neurology", title="Hidden Computational Power Found in the Arms of Neurons", content=content3, synopsis=generate_summary(content3,1), author=admin_profile)
  db.session.add(post3)
  
  content4='''Peak performance experts say things like, “You should focus. You need to eliminate the distractions. Commit to one thing and become great at that thing.”

This is good advice. The more I study successful people from all walks of life—artists, athletes, entrepreneurs, scientists—the more I believe focus is a core factor of success.

But there is a problem with this advice too.

Of the many options in front of you, how do you know what to focus on? How do you know where to direct your energy and attention? How do you determine the one thing that you should commit to doing?

I don’t claim to have all the answers, but let me share what I’ve learned so far.

“Until Something Comes Easily…”

Like most entrepreneurs, I struggled through my first year of building a business.

I launched my first product without having any idea who I would sell it to. (Big surprise, nobody bought it.) I reached out to important people, mismanaged expectations, made stupid mistakes, and essentially ruined the chance to build good relationships with people I respected. I attempted to teach myself how to code, made one change to my website, and deleted everything I had done during the previous three months.

To put it simply, I didn't know what I was doing.

During my Year of Many Errors I received a good piece of advice: “Try things until something comes easily.” I took the advice to heart and tried four or five different business ideas over the next 18 months. I'd give each one a shot for two or three months, mix in a little bit of freelance work so I could continue scraping by and paying the bills, and repeat the process.

Eventually, I found “something that came easily” and I was able to focus on building one business rather than trying to find an idea. In other words, I was able to simplify.

This was the first thing I discovered about figuring out what to focus on. If you want to master and deeply understand the core fundamentals of a task you may, paradoxically, need to start by casting a very wide net. By trying many different things, you can get a sense of what comes more easily to you and set yourself up for success. It is much easier to focus on something that's working than struggle along with a bad idea.

Make a Call About What to Focus On

Assuming you're willing to try things and experiment a bit, the next question is, “How do I know what's coming easily to me?”

The best answer I can give is to pay attention. Usually, this means measuring something.

If you're an entrepreneur, track your marketing and promotion efforts.
If you're trying to gain muscle, track your workouts.
If you're learning an instrument, track your practice sessions.
Even when you do measure things, however, there comes a point where you have to make a call and decide what to focus on.

In my mind, this moment of decision is one of the central tensions of entrepreneurship. Do we continue trying new things or do we double down on one strategy? Do we try to innovate or do we commit to doing one thing well?

Everyone wants to know the right time to simplify and focus on one thing, but nobody does. That's what makes success so hard. Entrepreneurship isn’t like baking a cake. There is no recipe. There is no guidebook.

At this stage, your best option is to decide. You can't try everything. At some point, you don't need more information, you just need to make a choice.

A Volume of Work

Now we have reached the stage where figuring out what to focus on becomes a real possibility.

You have experimented with enough ideas to discover one or two options that seem to provide better than average results for you. You've overcome the hurdle of wanting more information and the fear of committing to something and now you've made a choice. You took the job. You started the business. You signed up for the class. You're ready.

Welcome to the grind. It's time to put in a volume of work. Not just once or twice. Not just when it's easy. But a consistent, repeated volume of work. You have to fall in love with boredom and stay on the bus.

It is through this sheer number of repetitions that you'll come to understand the fundamentals of your task. You might know what greatness looks like before this point, but you won't understand how to achieve greatness until you've put the work in yourself.

In the words of Ira Glass, “your taste is good enough that you can tell that what you’re making is kind of a disappointment to you.” You'll bridge that gap between what you know is good and what you can produce yourself by putting in the reps.

This applies to so many areas of life.

Want to dress well and develop killer style? You’re going to have to try on a lot of clothes before you can simplify down to the essentials. You’ll probably have to buy a lot of clothes before you can really get a feel for what your day-in, day-out style is. I’m not a fan of promoting rampant consumerism, but if that’s the skill set you want to develop then it’s likely going to take some experimentation and effort.

Want to become a great cook? How many bad meals do you think you need to make before you can whip up a “simple, but tasty dinner” whenever you feel like it? I’d say hundreds at least. I don’t know many people who are amazing cooks after making their tenth meal ever. Developing a deep understanding of the fundamentals of cooking takes a while.

Want to write an amazing book? You're going to have to write and write and write some more. You need to write hundreds of thousands of words to find your voice, maybe millions. Then you need to edit those words and whittle them down to the most powerful version possible.

Only after the repetitions have been completed will you understand which pieces of the task are fundamental to success.

Getting to Simple

Now, finally, after trying many things and figuring out what to focus on and putting in enough reps, you can begin to simplify. You can trim away the fat because you know what is essential and what is unnecessary.

As the Frenchman Blaise Pascal famously wrote in his Provincial Letters, “If I had more time, I would have written you a shorter letter.”

Mastering the fundamentals is often the hardest and longest journey of all.'''
  post4 = blog_data(category="General Knowledge", title="How Experts Figure What to Focus On", content=content4, synopsis=generate_summary(content4,1), author=admin_profile)
  db.session.add(post4)
  
  db.session.commit()
  
  blog1_test_tag = Tag(name="CEP", blog_id = post1.id)
  blog2_test_tag = Tag(name="Computer Science", blog_id = post2.id)
  blog3_test_tag = Tag(name="Climate Change", blog_id = post2.id)
  blog4_test_tag = Tag(name="Neurology", blog_id = post2.id)
  blog5_test_tag = Tag(name="Biology", blog_id = post2.id)
  test_tag = Tag(name="other", blog_id = post1.id)
  
  db.session.add(blog1_test_tag)
  db.session.add(blog2_test_tag)
  db.session.add(blog3_test_tag)
  db.session.add(blog4_test_tag)
  db.session.add(blog5_test_tag)
  db.session.add(test_tag)
  db.session.commit()
  
  post1.tags.extend([blog1_test_tag, test_tag, blog3_test_tag, blog4_test_tag, blog5_test_tag])
  post2.tags.append(blog2_test_tag)
  
  db.session.commit()



  
